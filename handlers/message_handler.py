"""Message handler for processing text messages."""

from services.line_service import line_service
from services.sheets_service import sheets_service
from utils.flex_messages import FlexMessages


class MessageHandler:
    """Handler for processing text messages."""

    # Command keywords (includes Rich Menu # commands)
    COMMANDS = {
        "help": ["help", "ช่วยเหลือ", "วิธีใช้", "?", "#help"],
        "status": ["status", "สถานะ", "portfolio", "พอร์ต", "#status"],
        "plan": ["plan", "แผน", "dca", "ซื้อ", "#dca"],
        "record": ["#record"],
        "report": ["#report", "report"],
        "settings": ["#settings", "settings", "ตั้งค่า", "budget", "งบ"],
    }

    def handle(self, event) -> None:
        """Process a text message event.

        Args:
            event: LINE MessageEvent with text content
        """
        reply_token = event.reply_token
        user_id = event.source.user_id
        text = event.message.text.strip().lower()

        # Check for commands
        if self._is_command(text, "help"):
            self._reply_help(reply_token, user_id)
        elif self._is_command(text, "status"):
            self._reply_status(reply_token, user_id)
        elif self._is_command(text, "plan"):
            self._reply_dca(reply_token, user_id)
        elif self._is_command(text, "record"):
            self._reply_record_tip(reply_token)
        elif self._is_command(text, "report"):
            self._reply_report(reply_token, user_id)
        elif self._is_command(text, "settings"):
            self._reply_settings(reply_token)
        else:
            # Default: greet and explain
            self._reply_default(reply_token, user_id)

    def _is_command(self, text: str, command: str) -> bool:
        """Check if text matches a command."""
        keywords = self.COMMANDS.get(command, [])
        return any(kw in text for kw in keywords)

    def _reply_help(self, reply_token: str, user_id: str) -> None:
        """Reply with service status (health check)."""
        from utils.test_runner import run_all_tests
        from services.line_service import line_service as ls
        
        # Send initial message
        line_service.reply_text(reply_token, "🔍 กำลังตรวจสอบสถานะระบบ...")
        
        # Run tests
        try:
            result = run_all_tests()
            
            # Send status Flex Message
            status_flex = FlexMessages.service_status(
                services=result.services,
                total_tests=result.total_tests,
                passed=result.passed,
                failed=result.failed,
                timestamp=result.timestamp
            )
            
            # Push message to user (since reply already sent)
            ls.push_flex(user_id, "สถานะระบบ", status_flex)
            
        except Exception as e:
            # Fallback to error message
            error_msg = f"❌ ไม่สามารถตรวจสอบสถานะระบบได้\n\nError: {str(e)}"
            ls.push_text(user_id, error_msg)


    def _reply_status(self, reply_token: str, user_id: str) -> None:
        """Reply with portfolio status using visual Flex Messages with P/L."""
        from services.price_service import price_service, PriceError
        
        holdings = sheets_service.get_holdings_value(user_id)

        if not holdings:
            line_service.reply_text(
                reply_token,
                "📊 ยังไม่มีข้อมูลการลงทุน\n\nส่งรูปหน้าจอการซื้อขายมาเพื่อเริ่มบันทึกได้เลย 📸",
            )
            return

        try:
            # Get real-time prices and exchange rate
            tickers = list(holdings.keys())
            current_prices = price_service.get_prices_thb(tickers)
            usd_thb_rate = price_service.get_usd_thb_rate()
            
            # Check for missing prices - ERROR instead of fallback
            missing_tickers = [t for t in tickers if t not in current_prices]
            if missing_tickers:
                raise PriceError(f"ไม่สามารถดึงราคา: {', '.join(missing_tickers)}")
            
            # Calculate values with market prices
            holdings_data = []
            total_cost = 0
            total_current = 0
            type_values = {"GOLD": 0, "STOCK": 0, "CRYPTO": 0}
            
            for ticker, data in holdings.items():
                cost_basis = data["total_thb"]
                qty = data["quantity"]
                asset_type = data.get("asset_type") or FlexMessages.get_asset_type(ticker)
                
                current_value = qty * current_prices[ticker]
                
                pl_amount = current_value - cost_basis
                pl_percent = (pl_amount / cost_basis * 100) if cost_basis > 0 else 0
                
                total_cost += cost_basis
                total_current += current_value
                type_values[asset_type] += current_value
                
                holdings_data.append({
                    "ticker": ticker,
                    "quantity": qty,
                    "value": current_value,
                    "cost": cost_basis,
                    "pl_amount": pl_amount,
                    "pl_percent": pl_percent,
                    "asset_type": asset_type,
                })
            
            # Calculate total P/L
            total_pl = total_current - total_cost
            total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0
            
            # Calculate percentages based on current market value
            type_ratios = {}
            for asset_type, value in type_values.items():
                if value > 0:
                    type_ratios[asset_type] = (value / total_current) * 100
            
            for h in holdings_data:
                h["percentage"] = (h["value"] / total_current) * 100 if total_current > 0 else 0
            
            # Sort by value descending
            holdings_data.sort(key=lambda x: x["value"], reverse=True)
            
            # Send two Flex Messages as carousel with P/L
            carousel = {
                "type": "carousel",
                "contents": [
                    FlexMessages.portfolio_overview(
                        total_current, 
                        type_ratios, 
                        total_pl=total_pl,
                        total_pl_percent=total_pl_percent,
                        usd_thb_rate=usd_thb_rate
                    ),
                    FlexMessages.ticker_breakdown(holdings_data),
                ],
            }
            
            line_service.reply_flex(reply_token, "สถานะพอร์ตลงทุน", carousel)
            
        except PriceError as e:
            # Throw exception for GCP Error Reporting
            raise e

    def _reply_dca(self, reply_token: str, user_id: str) -> None:
        """Reply with Smart DCA plan using rebalance-by-buying logic."""
        from utils.dca_calculator import calculate_dca_rebalance, format_dca_message
        from services.price_service import price_service, PriceError
        
        user = sheets_service.get_user(user_id)
        
        if not user or not user.get("target_allocation"):
            line_service.reply_text(
                reply_token,
                "📋 ยังไม่ได้ตั้งค่าแผนลงทุน\n\nพิมพ์ #settings เพื่อตั้งค่างบและแผน",
            )
            return

        budget = user.get("monthly_budget", 10000)
        allocation = user.get("target_allocation", {})

        if not allocation:
            line_service.reply_text(
                reply_token,
                "📋 ยังไม่ได้ตั้งค่าสัดส่วนการลงทุน\n\nพิมพ์ #settings เพื่อตั้งค่า",
            )
            return

        try:
            # Get current holdings with quantities
            holdings = sheets_service.get_holdings_value(user_id)
            
            # Get real-time prices and calculate market values
            tickers = list(holdings.keys())
            current_prices = price_service.get_prices_thb(tickers)
            
            # Check for missing prices - ERROR instead of fallback
            missing_tickers = [t for t in tickers if t not in current_prices]
            if missing_tickers:
                raise PriceError(f"ไม่สามารถดึงราคา: {', '.join(missing_tickers)}")
            
            current_values = {}
            for asset, data in holdings.items():
                qty = data["quantity"]
                current_values[asset] = qty * current_prices[asset]
            
            # Calculate Smart DCA with market values
            result = calculate_dca_rebalance(
                monthly_budget=budget,
                target_allocation=allocation,
                current_holdings=current_values,
            )
            
            # Format and send
            message = format_dca_message(result)
            line_service.reply_text(reply_token, message)
            
        except PriceError as e:
            # Throw exception for GCP Error Reporting
            raise e

    def _reply_record_tip(self, reply_token: str) -> None:
        """Reply with tip to send image."""
        line_service.reply_text(
            reply_token,
            "📸 **บันทึกรายการ**\n\nส่งรูปหน้าจอการซื้อขายจาก:\n• Dime! (หุ้น US, ทอง)\n• Binance (คริปโต)\n\nมาได้เลย!",
        )

    def _reply_report(self, reply_token: str, user_id: str) -> None:
        """Reply with portfolio P/L report using real-time prices."""
        from services.price_service import price_service, PriceError
        
        holdings = sheets_service.get_holdings_value(user_id)
        
        if not holdings:
            line_service.reply_text(
                reply_token,
                "📈 ยังไม่มีข้อมูลการลงทุน\n\nส่งรูปหน้าจอการซื้อขายมาเพื่อเริ่มบันทึกได้เลย 📸",
            )
            return
        
        try:
            # Get tickers for price lookup and exchange rate
            tickers = list(holdings.keys())
            current_prices = price_service.get_prices_thb(tickers)
            usd_thb_rate = price_service.get_usd_thb_rate()
            
            # Check for missing prices - ERROR instead of fallback
            missing_tickers = [t for t in tickers if t not in current_prices]
            if missing_tickers:
                raise PriceError(f"ไม่สามารถดึงราคา: {', '.join(missing_tickers)}")
            
            # Calculate P/L for each holding
            total_cost = 0
            total_current = 0
            pl_data = []
            
            for ticker, data in holdings.items():
                cost_basis = data["total_thb"]
                qty = data["quantity"]
                asset_type = data.get("asset_type", "STOCK")
                
                current_value = qty * current_prices[ticker]
                
                pl_amount = current_value - cost_basis
                pl_percent = (pl_amount / cost_basis * 100) if cost_basis > 0 else 0
                
                total_cost += cost_basis
                total_current += current_value
                
                pl_data.append({
                    "ticker": ticker,
                    "cost": cost_basis,
                    "current": current_value,
                    "pl_amount": pl_amount,
                    "pl_percent": pl_percent,
                    "asset_type": asset_type,
                })
            
            # Sort by P/L amount descending
            pl_data.sort(key=lambda x: x["pl_amount"], reverse=True)
            
            # Calculate totals
            total_pl = total_current - total_cost
            total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0
            
            # Send P/L Flex Message
            pl_flex = FlexMessages.report_pl(
                total_cost=total_cost,
                total_current=total_current,
                total_pl=total_pl,
                total_pl_percent=total_pl_percent,
                holdings=pl_data,
                usd_thb_rate=usd_thb_rate,
            )
            line_service.reply_flex(reply_token, "รายงานกำไร/ขาดทุน", pl_flex)
            
        except PriceError as e:
            # Throw exception for GCP Error Reporting
            raise e

    def _reply_settings(self, reply_token: str) -> None:
        """Reply with budget selection."""
        line_service.reply_flex(
            reply_token,
            "ตั้งค่างบลงทุน",
            FlexMessages.budget_question(),
        )

    def _reply_default(self, reply_token: str, user_id: str) -> None:
        """Reply with default greeting."""
        # Check if user is new
        user = sheets_service.get_user(user_id)

        if user is None:
            # New user - get profile and create
            profile = line_service.get_profile(user_id)
            display_name = profile.get("display_name", "User") if profile else "User"
            sheets_service.create_user(user_id, display_name)

            # Send welcome message
            flex_content = FlexMessages.welcome_message(display_name)
            line_service.reply_flex(
                reply_token,
                f"ยินดีต้อนรับ {display_name}!",
                flex_content,
            )
        else:
            # Existing user - remind how to use
            line_service.reply_text(
                reply_token,
                "👋 สวัสดี!\n\n📸 ส่งรูปหน้าจอการซื้อขายมาได้เลย\n\nหรือพิมพ์ 'help' เพื่อดูคำสั่งทั้งหมด",
            )


# Singleton instance
message_handler = MessageHandler()
