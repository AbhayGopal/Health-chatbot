from typing import Dict, List

class AssessmentService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.assessment_templates = {
            'sleep': self._get_sleep_assessment(),
            'sexual_health': self._get_sexual_health_assessment(),
            'general_health': self._get_general_health_assessment()
        }
        
    def _get_sleep_assessment(self) -> Dict:
        return {
            'questions': [
                {
                    'id': 'sleep_1',
                    'text': 'How many hours do you typically sleep per night?',
                    'options': ['Less than 5', '5-6', '7-8', 'More than 8'],
                    'weights': [1, 2, 4, 3]
                },
                {
                    'id': 'sleep_2',
                    'text': 'How often do you have trouble falling asleep?',
                    'options': ['Never', 'Sometimes', 'Often', 'Always'],
                    'weights': [4, 3, 2, 1]
                },
                {
                    'id': 'sleep_3',
                    'text': 'Do you feel refreshed when you wake up?',
                    'options': ['Always', 'Usually', 'Rarely', 'Never'],
                    'weights': [4, 3, 2, 1]
                }
            ],
            'max_score': 12
        }
    
    def _get_sexual_health_assessment(self) -> Dict:
        return {
            'questions': [
                {
                    'id': 'sexual_1',
                    'text': 'How would you rate your overall sexual health?',
                    'options': ['Excellent', 'Good', 'Fair', 'Poor'],
                    'weights': [4, 3, 2, 1]
                }
            ],
            'max_score': 4
        }
    
    def _get_general_health_assessment(self) -> Dict:
        return {
            'questions': [
                {
                    'id': 'general_1',
                    'text': 'How would you rate your overall health?',
                    'options': ['Excellent', 'Good', 'Fair', 'Poor'],
                    'weights': [4, 3, 2, 1]
                }
            ],
            'max_score': 4
        }
    
    def get_assessment(self, category: str) -> Dict:
        """Get assessment questions for a specific category"""
        return self.assessment_templates.get(category, self.assessment_templates['general_health'])
    
    def calculate_score(self, category: str, answers: Dict[str, str]) -> Dict:
        """Calculate assessment score and provide recommendations"""
        template = self.assessment_templates.get(category)
        if not template:
            return {"error": "Invalid category"}
            
        total_score = 0
        max_score = template['max_score']
        
        for question in template['questions']:
            answer = answers.get(question['id'])
            if answer:
                try:
                    answer_index = question['options'].index(answer)
                    total_score += question['weights'][answer_index]
                except (ValueError, IndexError):
                    continue
        
        score_percentage = (total_score / max_score) * 100
        
        return {
            "score": score_percentage,
            "recommendations": self._get_recommendations(category, score_percentage),
            "related_products": self._get_recommended_products(category, score_percentage)
        }
    
    def _get_recommendations(self, category: str, score: float) -> List[str]:
        """Get recommendations based on assessment score"""
        if score >= 80:
            return ["Your health appears to be good! Here are some tips to maintain it..."]
        elif score >= 60:
            return ["There's room for improvement. Consider these suggestions..."]
        else:
            return ["We recommend consulting with a healthcare professional for personalized advice."]
    
    def _get_recommended_products(self, category: str, score: float) -> List[Dict]:
        """Get product recommendations based on assessment results"""
        return self.db_manager.get_products_by_category(category)