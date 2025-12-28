"""AI Insight Service using Gemini for personalized portfolio analysis."""

from typing import Optional
from google import genai
from config import Config


class AIInsightService:
    """Service for generating AI-powered portfolio insights."""
    
    def __init__(self):
        self._client: Optional[genai.Client] = None
    
    @property
    def client(self) -> genai.Client:
        """Lazy-load the Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=Config.GEMINI_API_KEY)
        return self._client
    
    def get_rebalance_insight(self, portfolio_data: dict) -> str:
        """Generate AI insight for portfolio rebalancing.
        
        Args:
            portfolio_data: Dict containing:
                - actions: List of rebalance actions with drift info
                - total_portfolio: Total portfolio value in THB
                - threshold: Drift threshold used
                
        Returns:
            Thai language insight/recommendation string
        """
        if not portfolio_data.get("actions"):
            return "ไม่มีข้อมูลเพียงพอสำหรับการวิเคราะห์"
        
        # Build context for AI
        actions = portfolio_data["actions"]
        total_value = portfolio_data.get("total_portfolio", 0)
        
        # Format portfolio summary
        portfolio_summary = []
        for action in actions:
            status_text = {
                "overweight": "น้ำหนักเกิน",
                "underweight": "น้ำหนักต่ำ", 
                "balanced": "สมดุล"
            }.get(action["status"], "ไม่ทราบ")
            
            portfolio_summary.append(
                f"- {action['asset']}: ปัจจุบัน {action['current_pct']:.1f}% "
                f"เป้า {action['target_pct']:.1f}% ({status_text})"
            )
        
        prompt = f"""คุณเป็นที่ปรึกษาการลงทุนส่วนบุคคล วิเคราะห์พอร์ตโฟลิโอนี้และให้คำแนะนำสั้นๆ:

มูลค่าพอร์ต: ฿{total_value:,.0f}

สถานะสินทรัพย์:
{chr(10).join(portfolio_summary)}

ให้คำแนะนำ 2-3 ประโยคเป็นภาษาไทย เน้น:
1. ควรปรับสมดุลอย่างไร
2. ข้อควรระวังหรือโอกาส
3. กลยุทธ์การทยอยซื้อ/ขาย (ถ้ามี)

ตอบแบบกระชับ เป็นกันเอง ไม่เกิน 100 คำ"""

        try:
            response = self.client.models.generate_content(
                model=Config.GEMINI_RESEARCH_MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            print(f"AI insight error: {e}")
            return "ไม่สามารถวิเคราะห์ได้ในขณะนี้"


# Singleton instance
ai_insight_service = AIInsightService()
