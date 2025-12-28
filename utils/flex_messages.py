"""LINE Flex Message templates."""


class FlexMessages:
    """Factory for creating LINE Flex Messages."""

    @staticmethod
    def transaction_confirmation(tx_data: dict) -> dict:
        """Create a transaction confirmation bubble."""
        side = tx_data.get("side", "BUY")
        side_color = "#00C853" if side == "BUY" else "#FF5252"
        side_emoji = "🟢" if side == "BUY" else "🔴"

        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "✅ บันทึกรายการสำเร็จ",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#1DB446",
                    }
                ],
                "backgroundColor": "#E8F5E9",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"{side_emoji} {side}",
                                "weight": "bold",
                                "size": "xl",
                                "color": side_color,
                            },
                            {
                                "type": "text",
                                "text": tx_data.get("asset_raw", tx_data.get("asset", "")),
                                "weight": "bold",
                                "size": "xl",
                                "align": "end",
                            },
                        ],
                    },
                    {"type": "separator", "margin": "lg"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            FlexMessages._info_row(
                                "จำนวน", f"{tx_data.get('amount', 0):,.4f}"
                            ),
                            FlexMessages._info_row(
                                "ราคา", f"{'$' if tx_data.get('original_currency') in ('USD', 'USDT') else '฿'}{tx_data.get('price', 0):,.2f}"
                            ),
                            FlexMessages._info_row(
                                "มูลค่ารวม", f"฿{tx_data.get('total_thb', 0):,.2f}"
                            ),
                            FlexMessages._info_row(
                                "แหล่งที่มา", tx_data.get("source_app", "")
                            ),
                            FlexMessages._info_row("วันที่", tx_data.get("date", "")),
                        ] + ([FlexMessages._info_row(
                                "💱 อัตราแลกเปลี่ยน", f"$1 = ฿{tx_data.get('usd_thb_rate', 0):.2f}"
                            )] if tx_data.get('original_currency') in ('USD', 'USDT') else []),
                    },
                ],
                "paddingAll": "15px",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ส่งสลิปเพิ่มเติมได้เลย 📸",
                        "size": "sm",
                        "color": "#888888",
                        "align": "center",
                    }
                ],
                "paddingAll": "10px",
            },
        }

    @staticmethod
    def _info_row(label: str, value: str) -> dict:
        """Create an info row for Flex Message."""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "sm",
                    "color": "#888888",
                    "flex": 2,
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "sm",
                    "color": "#333333",
                    "align": "end",
                    "flex": 3,
                },
            ],
        }

    @staticmethod
    def error_message(title: str, message: str) -> dict:
        """Create an error message bubble."""
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"❌ {title}",
                        "weight": "bold",
                        "size": "md",
                        "color": "#D32F2F",
                    }
                ],
                "backgroundColor": "#FFEBEE",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": message,
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                    }
                ],
                "paddingAll": "15px",
            },
        }

    @staticmethod
    def welcome_message(display_name: str) -> dict:
        """Create a welcome message for new users."""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🎉 ยินดีต้อนรับ!",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFF",
                    },
                    {
                        "type": "text",
                        "text": f"สวัสดี {display_name}",
                        "size": "md",
                        "color": "#FFFFFF",
                        "margin": "sm",
                    },
                ],
                "backgroundColor": "#6366F1",
                "paddingAll": "20px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Opes AI พร้อมช่วยจัดการการลงทุนของคุณแล้ว!",
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                    },
                    {"type": "separator", "margin": "lg"},
                    {
                        "type": "text",
                        "text": "📸 ส่งรูปหน้าจอการซื้อขาย",
                        "size": "sm",
                        "color": "#333333",
                        "margin": "lg",
                        "weight": "bold",
                    },
                    {
                        "type": "text",
                        "text": "จาก Dime! หรือ Binance ได้เลย",
                        "size": "xs",
                        "color": "#888888",
                        "margin": "sm",
                    },
                ],
                "paddingAll": "20px",
            },
        }

    @staticmethod
    def welcome_new_user(display_name: str) -> dict:
        """Create a welcome message for new users with onboarding CTA."""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🎉 ยินดีต้อนรับ!",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFF",
                    },
                    {
                        "type": "text",
                        "text": f"สวัสดี {display_name}",
                        "size": "md",
                        "color": "#FFFFFF",
                        "margin": "sm",
                    },
                ],
                "backgroundColor": "#6366F1",
                "paddingAll": "20px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Opes AI พร้อมช่วยจัดการพอร์ตลงทุนของคุณ",
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                    },
                    {"type": "separator", "margin": "lg"},
                    {
                        "type": "text",
                        "text": "⚙️ ตั้งค่างบและแผนลงทุน",
                        "size": "sm",
                        "color": "#333333",
                        "margin": "lg",
                        "weight": "bold",
                    },
                    {
                        "type": "text",
                        "text": "เพื่อให้ระบบช่วยคำนวณแผน DCA ให้คุณ",
                        "size": "xs",
                        "color": "#888888",
                        "margin": "sm",
                    },
                ],
                "paddingAll": "20px",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "เริ่มตั้งค่า",
                            "data": "start_onboarding",
                        },
                        "color": "#6366F1",
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "action": {
                            "type": "postback",
                            "label": "ข้ามไปก่อน ส่งรูปเลย",
                            "data": "skip_onboarding",
                        },
                    },
                ],
                "paddingAll": "15px",
            },
        }

    @staticmethod
    def welcome_back_message(display_name: str) -> dict:
        """Create a welcome back message for returning users."""
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"👋 ยินดีต้อนรับกลับ {display_name}!",
                        "weight": "bold",
                        "color": "#FFFFFF",
                        "size": "md",
                    }
                ],
                "backgroundColor": "#6366F1",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📸 ส่งรูปสลิปมาได้เลย หรือใช้ Rich Menu ด้านล่าง",
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                    }
                ],
                "paddingAll": "15px",
            },
        }



    @staticmethod
    def setup_plan_prompt() -> dict:
        """Create a prompt to set up investment plan via LIFF."""
        from config import Config
        liff_url = Config.LIFF_URL
        
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "⚙️ ตั้งค่าแผนลงทุน",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#333333",
                    }
                ],
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "กำหนดงบและสัดส่วนการลงทุนของคุณ",
                        "wrap": True,
                        "color": "#666666",
                        "size": "sm",
                    },
                    {
                        "type": "text",
                        "text": "• ตั้งงบลงทุนต่อเดือน\n• เลือกสินทรัพย์และสัดส่วน\n• ระบบจะคำนวณแผน DCA ให้",
                        "wrap": True,
                        "color": "#888888",
                        "size": "xs",
                        "margin": "md",
                    },
                ],
                "paddingAll": "15px",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "ตั้งค่าแผน",
                            "uri": liff_url,
                        },
                        "color": "#6366F1",
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "action": {
                            "type": "postback",
                            "label": "ข้ามไปก่อน",
                            "data": "skip_onboarding",
                        },
                        "margin": "sm",
                    },
                ],
                "paddingAll": "15px",
            },
        }

    # Asset type colors
    ASSET_COLORS = {
        "STOCK": "#10B981",      # Green
        "CRYPTO": "#6366F1",     # Purple
        "GOLD": "#F59E0B",    # Orange
        "CASH": "#6B7280",      # Gray
    }

    @staticmethod
    def get_asset_type(ticker: str) -> str:
        """Determine asset type from ticker."""
        gold_tickers = {"GOLD", "XAUUSD", "XAU"}
        crypto_tickers = {"BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "DOT", "MATIC"}
        
        if ticker.upper() in gold_tickers:
            return "GOLD"
        elif ticker.upper() in crypto_tickers:
            return "CRYPTO"
        else:
            return "STOCK"

    @classmethod
    def portfolio_overview(cls, total_value: float, type_ratios: dict, total_pl: float = None, total_pl_percent: float = None, usd_thb_rate: float = None) -> dict:
        """Create portfolio overview Flex Message with asset type ratio bar.
        
        Args:
            total_value: Total portfolio value in THB
            type_ratios: Dict of {asset_type: percentage}, e.g. {"GOLD": 30, "STOCK": 40, "CRYPTO": 30}
            total_pl: Optional total P/L amount in THB
            total_pl_percent: Optional total P/L percentage
            usd_thb_rate: Optional USD/THB exchange rate to display
        """
        # Build ratio bar segments
        bar_segments = []
        for asset_type, pct in type_ratios.items():
            if pct > 0:
                bar_segments.append({
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "flex": int(pct),
                    "backgroundColor": cls.ASSET_COLORS.get(asset_type, "#6B7280"),
                })
        
        # Build legend items
        legend_items = []
        type_labels = {"GOLD": "ทอง", "STOCK": "หุ้น", "CRYPTO": "คริปโต", "CASH": "เงินสด"}
        for asset_type, pct in type_ratios.items():
            if pct > 0:
                legend_items.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "width": "10px",
                            "height": "10px",
                            "backgroundColor": cls.ASSET_COLORS.get(asset_type, "#6B7280"),
                            "cornerRadius": "5px",
                        },
                        {
                            "type": "text",
                            "text": f"{pct:.0f}% {type_labels.get(asset_type, asset_type)}",
                            "size": "xs",
                            "color": "#666666",
                            "margin": "sm",
                        },
                    ],
                    "alignItems": "center",
                })
        
        # Build P/L indicator if provided
        pl_content = []
        if total_pl is not None and total_pl_percent is not None:
            is_profit = total_pl >= 0
            pl_color = "#10B981" if is_profit else "#EF4444"
            pl_emoji = "🟢" if is_profit else "🔴"
            pl_sign = "+" if is_profit else ""
            
            pl_content = [
                {"type": "separator", "margin": "lg"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"{pl_emoji} กำไร/ขาดทุน", "size": "sm", "color": "#666666", "flex": 1},
                        {"type": "text", "text": f"{pl_sign}{total_pl_percent:.2f}% ({pl_sign}฿{abs(total_pl):,.0f})", "size": "sm", "weight": "bold", "color": pl_color, "align": "end"},
                    ],
                    "margin": "lg",
                },
            ]
        
        result = {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 สถานะพอร์ตลงทุน",
                        "weight": "bold",
                        "size": "md",
                        "color": "#FFFFFF",
                    }
                ],
                "backgroundColor": "#1F2937",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "มูลค่ารวม",
                        "size": "sm",
                        "color": "#888888",
                    },
                    {
                        "type": "text",
                        "text": f"฿{total_value:,.0f}",
                        "size": "xxl",
                        "weight": "bold",
                        "color": "#333333",
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": bar_segments if bar_segments else [{"type": "filler"}],
                        "height": "12px",
                        "cornerRadius": "6px",
                        "margin": "lg",
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": legend_items if legend_items else [{"type": "filler"}],
                        "margin": "md",
                        "spacing": "lg",
                    },
                ] + pl_content,
                "paddingAll": "15px",
            },
        }
        
        if usd_thb_rate:
            result["footer"] = {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"$1 = ฿{usd_thb_rate:.2f}",
                        "size": "xs",
                        "color": "#888888",
                        "align": "center",
                    }
                ],
                "paddingAll": "8px",
            }
        
        return result

    @classmethod
    def ticker_breakdown(cls, holdings: list) -> dict:
        """Create ticker breakdown Flex Message with individual progress bars.
        
        Args:
            holdings: List of dicts with {ticker, value, percentage, asset_type}
        """
        ticker_items = []
        
        for h in holdings:
            ticker = h["ticker"]
            value = h["value"]
            pct = h["percentage"]
            asset_type = h.get("asset_type", cls.get_asset_type(ticker))
            color = cls.ASSET_COLORS.get(asset_type, "#6B7280")
            
            # Progress bar
            filled = max(1, int(pct))
            unfilled = max(1, 100 - filled)
            
            ticker_items.extend([
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": ticker,
                            "weight": "bold",
                            "size": "sm",
                            "flex": 1,
                        },
                        {
                            "type": "text",
                            "text": f"฿{value:,.0f} ({pct:.0f}%)",
                            "size": "sm",
                            "color": "#666666",
                            "align": "end",
                        },
                    ],
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "flex": filled,
                            "backgroundColor": color,
                            "height": "8px",
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "flex": unfilled,
                            "backgroundColor": "#E5E7EB",
                            "height": "8px",
                        },
                    ],
                    "cornerRadius": "4px",
                    "margin": "xs",
                },
                {"type": "separator", "margin": "md"},
            ])
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📈 รายละเอียดสินทรัพย์",
                        "weight": "bold",
                        "size": "md",
                        "color": "#FFFFFF",
                    }
                ],
                "backgroundColor": "#1F2937",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": ticker_items if ticker_items else [
                    {"type": "text", "text": "ยังไม่มีสินทรัพย์", "color": "#888888"}
                ],
                "paddingAll": "15px",
            },
        }

    @classmethod
    def report_pl(
        cls, 
        total_cost: float, 
        total_current: float, 
        total_pl: float, 
        total_pl_percent: float,
        holdings: list,
        usd_thb_rate: float = None
    ) -> dict:
        """Create P/L report Flex Message.
        
        Args:
            total_cost: Total cost basis in THB
            total_current: Total current value in THB
            total_pl: Total P/L amount in THB
            total_pl_percent: Total P/L percentage
            holdings: List of dicts with ticker, cost, current, pl_amount, pl_percent
            usd_thb_rate: Optional USD/THB exchange rate to display
        """
        # Determine profit or loss color
        is_profit = total_pl >= 0
        pl_color = "#10B981" if is_profit else "#EF4444"  # Green or Red
        pl_emoji = "🟢" if is_profit else "🔴"
        pl_sign = "+" if is_profit else ""
        
        # Build holdings items
        holdings_items = []
        for h in holdings:
            h_profit = h["pl_amount"] >= 0
            h_color = "#10B981" if h_profit else "#EF4444"
            h_sign = "+" if h_profit else ""
            
            holdings_items.extend([
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": h["ticker"], "weight": "bold", "size": "sm", "flex": 1},
                        {"type": "text", "text": f"{h_sign}{h['pl_percent']:.2f}%", "weight": "bold", "color": h_color, "size": "sm", "align": "end"},
                    ],
                    "margin": "lg",
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"฿{h['cost']:,.0f} → ฿{h['current']:,.0f}", "size": "xs", "color": "#888888", "flex": 1},
                        {"type": "text", "text": f"({h_sign}฿{abs(h['pl_amount']):,.0f})", "size": "xs", "color": h_color, "align": "end"},
                    ],
                    "margin": "xs",
                },
                {"type": "separator", "margin": "md"},
            ])
        
        result = {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "📈 รายงานกำไร/ขาดทุน", "weight": "bold", "size": "lg", "color": "#FFFFFF"},
                ],
                "backgroundColor": "#1F2937",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # Summary section
                    {"type": "text", "text": "สรุป", "weight": "bold", "size": "md", "margin": "none"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "ต้นทุน", "size": "sm", "color": "#666666", "flex": 1},
                            {"type": "text", "text": f"฿{total_cost:,.0f}", "size": "sm", "align": "end"},
                        ],
                        "margin": "md",
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "มูลค่าปัจจุบัน", "size": "sm", "color": "#666666", "flex": 1},
                            {"type": "text", "text": f"฿{total_current:,.0f}", "size": "sm", "align": "end"},
                        ],
                        "margin": "sm",
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": f"{pl_emoji} กำไร/ขาดทุน", "weight": "bold", "size": "md", "flex": 1},
                            {"type": "text", "text": f"{pl_sign}{total_pl_percent:.2f}% ({pl_sign}฿{abs(total_pl):,.0f})", "weight": "bold", "size": "md", "color": pl_color, "align": "end"},
                        ],
                        "margin": "lg",
                    },
                    {"type": "separator", "margin": "lg"},
                    # Holdings detail
                    {"type": "text", "text": "รายละเอียด", "weight": "bold", "size": "md", "margin": "lg"},
                ] + holdings_items,
                "paddingAll": "15px",
            },
        }
        
        if usd_thb_rate:
            result["footer"] = {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"อัตราแลกเปลี่ยน $1 = ฿{usd_thb_rate:.2f}",
                        "size": "xs",
                        "color": "#888888",
                        "align": "center",
                    }
                ],
                "paddingAll": "8px",
            }
        
        return result

    @staticmethod
    def service_status(services: dict, total_tests: int, passed: int, failed: int, timestamp) -> dict:
        """Create service status Flex Message.
        
        Args:
            services: Dict of {service_name: is_healthy}
            total_tests: Total number of tests run
            passed: Number of passed tests
            failed: Number of failed tests
            timestamp: datetime of status check
        """
        # Build service status items
        service_items = []
        all_healthy = all(services.values())
        
        for service_name, is_healthy in services.items():
            status_emoji = "✅" if is_healthy else "❌"
            status_color = "#10B981" if is_healthy else "#EF4444"
            
            service_items.extend([
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": status_emoji,
                            "size": "md",
                            "flex": 0,
                        },
                        {
                            "type": "text",
                            "text": service_name,
                            "size": "sm",
                            "color": status_color,
                            "margin": "md",
                            "flex": 1,
                        },
                    ],
                    "margin": "md",
                },
            ])
        
        # Overall status
        overall_emoji = "🟢" if all_healthy else "🔴"
        overall_text = "ระบบทำงานปกติ" if all_healthy else "ตรวจพบปัญหา"
        overall_color = "#10B981" if all_healthy else "#EF4444"
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🔧 สถานะระบบ",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF",
                    }
                ],
                "backgroundColor": "#1F2937",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": overall_emoji,
                                "size": "xl",
                                "flex": 0,
                            },
                            {
                                "type": "text",
                                "text": overall_text,
                                "size": "md",
                                "weight": "bold",
                                "color": overall_color,
                                "margin": "md",
                            },
                        ],
                        "margin": "none",
                    },
                    {"type": "separator", "margin": "lg"},
                    {
                        "type": "text",
                        "text": "บริการ",
                        "size": "sm",
                        "color": "#666666",
                        "weight": "bold",
                        "margin": "lg",
                    },
                ] + service_items,
                "paddingAll": "15px",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"Tests: {passed}/{total_tests} passed",
                        "size": "xs",
                        "color": "#888888",
                        "align": "center",
                    },
                    {
                        "type": "text",
                        "text": f"Last checked: {timestamp.strftime('%Y-%m-%d %H:%M')}",
                        "size": "xs",
                        "color": "#888888",
                        "align": "center",
                        "margin": "xs",
                    },
                ],
                "paddingAll": "10px",
            },
        }

    @staticmethod
    def ai_features_menu() -> dict:
        """Create AI Features Menu Flex Message with action buttons."""
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🤖 AI Features",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF",
                    }
                ],
                "backgroundColor": "#6366F1",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "เลือกฟีเจอร์ AI ที่ต้องการใช้งาน",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "none",
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "📊 Rebalance Analysis",
                            "text": "#rebalance",
                        },
                        "style": "primary",
                        "color": "#10B981",
                        "margin": "lg",
                        "height": "sm",
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "🔍 Research Asset (เร็วๆนี้)",
                            "text": "#research",
                        },
                        "style": "secondary",
                        "margin": "md",
                        "height": "sm",
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "📈 Market Insights (เร็วๆนี้)",
                            "text": "#insights",
                        },
                        "style": "secondary",
                        "margin": "md",
                        "height": "sm",
                    },
                ],
                "paddingAll": "15px",
            },
        }

    @staticmethod
    def rebalance_report(result: dict, usd_thb_rate: float) -> dict:
        """Create Rebalance Report Flex Message with actionable instructions."""
        
        if "error" in result:
            return {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"❌ {result['error']}", "wrap": True}
                    ],
                },
            }
        
        actions = result["actions"]
        drift_count = result["total_drift_assets"]
        
        # Header status
        if drift_count == 0:
            header_text = "✅ พอร์ตสมดุลดี"
            header_color = "#10B981"
        else:
            header_text = f"⚠️ พบการเบี่ยงเบน {drift_count} รายการ"
            header_color = "#F59E0B"
        
        # Build action items
        action_contents = []
        
        for action in actions:
            if action["status"] == "balanced":
                emoji = "⚪"
                status_text = "✓ สมดุล"
                color = "#6B7280"
            elif action["status"] == "overweight":
                emoji = "🔴"
                status_text = f"เกิน +{action['drift']:.0f}%"
                color = "#EF4444"
            else:  # underweight
                emoji = "🟢"
                status_text = f"ต่ำ {action['drift']:.0f}%"
                color = "#10B981"
            
            # Asset header
            action_contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "text", "text": f"{emoji} {action['asset']}", "weight": "bold", "size": "sm", "flex": 1},
                    {"type": "text", "text": f"{action['current_pct']:.0f}% → {action['target_pct']:.0f}%", "size": "xs", "color": "#666666", "align": "end"},
                ],
                "margin": "lg",
            })
            
            # Action instruction (only if not balanced)
            if action["status"] != "balanced" and action["qty_to_trade"] > 0:
                action_type = "ขาย" if action["action_type"] == "sell" else "ซื้อเพิ่ม"
                
                # Format quantity based on asset type
                if action["asset"] in ["BTC", "ETH", "SOL"]:
                    qty_text = f"{action['qty_to_trade']:.6f}"
                else:
                    qty_text = f"{action['qty_to_trade']:.2f}"
                
                thb_amount = action["value_thb"]
                usd_amount = action["value_usd"]
                
                action_contents.append({
                    "type": "text",
                    "text": f"   📌 {action_type}: {qty_text} (~฿{thb_amount:,.0f} / ${usd_amount:,.0f})",
                    "size": "xs",
                    "color": color,
                    "margin": "sm",
                })
            elif action["status"] == "balanced":
                action_contents.append({
                    "type": "text",
                    "text": f"   {status_text}",
                    "size": "xs",
                    "color": color,
                    "margin": "sm",
                })
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "📊 Rebalance Report", "weight": "bold", "size": "lg", "color": "#FFFFFF"}
                ],
                "backgroundColor": "#1F2937",
                "paddingAll": "15px",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": header_text, "weight": "bold", "size": "md", "color": header_color},
                    {"type": "separator", "margin": "lg"},
                ] + action_contents,
                "paddingAll": "15px",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"Threshold: ±{result['threshold']:.0f}%", "size": "xs", "color": "#888888", "align": "center"},
                ],
                "paddingAll": "10px",
            },
        }
