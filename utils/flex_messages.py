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
                                "ราคา", f"฿{tx_data.get('price', 0):,.2f}"
                            ),
                            FlexMessages._info_row(
                                "มูลค่ารวม", f"฿{tx_data.get('total_thb', 0):,.2f}"
                            ),
                            FlexMessages._info_row(
                                "แหล่งที่มา", tx_data.get("source_app", "")
                            ),
                            FlexMessages._info_row("วันที่", tx_data.get("date", "")),
                        ],
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
                        "text": "Family Wealth AI พร้อมช่วยจัดการการลงทุนของคุณแล้ว!",
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
                        "text": "Family Wealth AI พร้อมช่วยจัดการพอร์ตลงทุนของคุณ",
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
    def budget_question() -> dict:
        """Create budget selection message."""
        budgets = [5000, 10000, 20000, 50000]
        buttons = [
            {
                "type": "button",
                "style": "secondary",
                "action": {
                    "type": "postback",
                    "label": f"฿{b:,}",
                    "data": f"set_budget={b}",
                },
                "height": "sm",
            }
            for b in budgets
        ]
        
        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "💰 งบลงทุนต่อเดือน",
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
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "เลือกงบที่ต้องการลงทุนต่อเดือน",
                        "size": "sm",
                        "color": "#888888",
                    },
                    {"type": "separator", "margin": "md"},
                    *buttons,
                ],
                "paddingAll": "15px",
            },
        }

    @staticmethod
    def allocation_setup_prompt(budget: int, liff_url: str = None) -> dict:
        """Create allocation setup prompt with LIFF link."""
        from config import Config
        if liff_url is None:
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
                        "text": "📊 ตั้งค่าแผนลงทุน",
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
                        "text": f"งบต่อเดือน: ฿{budget:,}",
                        "size": "md",
                        "color": "#6366F1",
                        "weight": "bold",
                    },
                    {
                        "type": "text",
                        "text": "ใส่ Ticker และน้ำหนัก % ของแต่ละสินทรัพย์ที่ต้องการลงทุน",
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
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
                        "type": "text",
                        "text": "หรือพิมพ์ #plan ทีหลังได้",
                        "size": "xs",
                        "color": "#888888",
                        "align": "center",
                        "margin": "md",
                    },
                ],
                "paddingAll": "15px",
            },
        }
