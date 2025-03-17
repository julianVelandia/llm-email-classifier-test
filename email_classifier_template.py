# Configuration and imports
import logging
import os
from typing import Dict, Optional

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample email dataset
sample_emails = [
    {
        "id": "001",
        "from": "angry.customer@example.com",
        "subject": "Broken product received",
        "body": "I received my order #12345 yesterday but it arrived completely damaged. This is unacceptable and I demand a refund immediately. This is the worst customer service I've experienced.",
        "timestamp": "2024-03-15T10:30:00Z"
    },
    {
        "id": "002",
        "from": "curious.shopper@example.com",
        "subject": "Question about product specifications",
        "body": "Hi, I'm interested in buying your premium package but I couldn't find information about whether it's compatible with Mac OS. Could you please clarify this? Thanks!",
        "timestamp": "2024-03-15T11:45:00Z"
    },
    {
        "id": "003",
        "from": "happy.user@example.com",
        "subject": "Amazing customer support",
        "body": "I just wanted to say thank you for the excellent support I received from Sarah on your team. She went above and beyond to help resolve my issue. Keep up the great work!",
        "timestamp": "2024-03-15T13:15:00Z"
    },
    {
        "id": "004",
        "from": "tech.user@example.com",
        "subject": "Need help with installation",
        "body": "I've been trying to install the software for the past hour but keep getting error code 5123. I've already tried restarting my computer and clearing the cache. Please help!",
        "timestamp": "2024-03-15T14:20:00Z"
    },
    {
        "id": "005",
        "from": "business.client@example.com",
        "subject": "Partnership opportunity",
        "body": "Our company is interested in exploring potential partnership opportunities with your organization. Would it be possible to schedule a call next week to discuss this further?",
        "timestamp": "2024-03-15T15:00:00Z"
    }
]


class EmailProcessor:
    def __init__(self):
        """Initialize the email processor with OpenAI API key."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define valid categories
        self.valid_categories = {
            "complaint", "inquiry", "feedback",
            "support_request", "other"
        }

        self.model = "gpt-4o"

    def classify_email(self, email: Dict) -> Optional[str]:
        """
        Classify an email using LLM.
        Returns the classification category or None if classification fails.

        1. Design and implement the classification prompt
        2. Make the API call with appropriate error handling
        3. Validate and return the classification
        """
        prompt = (
            "Please classify the following email as one of the following categories: "
            f"{', '.join(self.valid_categories)}"
            f"\nSubject: {email['subject']}\nBody: {email['body']}"
            "Return only the category or None if classification fails (JUST THE CATEGORY, NO QUOTES)"
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            category_as_a_text = completion.choices[0].message.content.strip().lower()
            return category_as_a_text if category_as_a_text in self.valid_categories else None
        except Exception as e:
            logger.error(f"Error with the LLM provider: {e}")
            return None

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate an automated response based on email classification.
        
        1. Design the response generation prompt
        2. Implement appropriate response templates
        3. Add error handling
        """
        prompt = (
            "Generate an automated response based on email classification"
            f"The category is {classification}"
            f"\nSubject: {email['subject']}\nBody: {email['body']}"
            "Return only the message (JUST THE MESSAGE, NO EXTRA TEXT)"
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error with the LLM provider: {e}")
            return None


class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        """Initialize the automation system with an EmailProcessor."""
        self.processor = processor
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other
        }

    def process_email(self, email: Dict) -> Dict:
        """
        Process a single email through the complete pipeline.
        Returns a dictionary with the processing results.
        
        1. Implement the complete processing pipeline
        2. Add appropriate error handling
        3. Return processing results
        """
        classification = self.processor.classify_email(email)
        if not classification:
            return {"email_id": email["id"], "success": False, "classification": None, "response_sent": False}
        handler = self.response_handlers.get(classification, self._handle_other)

        response = handler(email)

        return {
            "email_id": email["id"],
            "success": True,
            "classification": classification,
            "response_sent": response
        }

    def _handle_complaint(self, email: Dict):
        """
        Handle complaint emails.
        """
        response = self.processor.generate_response(email, "complaint")
        send_complaint_response(email["id"], response)
        return response


    def _handle_inquiry(self, email: Dict):
        """
        Handle inquiry emails.
        """
        response = self.processor.generate_response(email, "inquiry")
        send_standard_response(email["id"], response)
        return response


    def _handle_feedback(self, email: Dict):
        """
        Handle feedback emails.
        """
        response = self.processor.generate_response(email, "feedback")
        log_customer_feedback(email["id"], response)
        return response


    def _handle_support_request(self, email: Dict):
        """
        Handle support request emails.
        """
        response = self.processor.generate_response(email, "support_request")
        create_support_ticket(email["id"], response)
        return response


    def _handle_other(self, email: Dict):
        """
        Handle other category emails.
        """
        # We have to return a response generated by LLM? or a default message
        response = self.processor.generate_response(email, "other")
        send_standard_response(email["id"], response)
        return response



# Mock service functions
def send_complaint_response(email_id: str, response: str):
    """Mock function to simulate sending a response to a complaint"""
    logger.info(f"Sending complaint response for email {email_id}")
    # In real implementation: integrate with email service


def send_standard_response(email_id: str, response: str):
    """Mock function to simulate sending a standard response"""
    logger.info(f"Sending standard response for email {email_id}")
    # In real implementation: integrate with email service


def create_urgent_ticket(email_id: str, category: str, context: str):
    """Mock function to simulate creating an urgent ticket"""
    logger.info(f"Creating urgent ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def create_support_ticket(email_id: str, context: str):
    """Mock function to simulate creating a support ticket"""
    logger.info(f"Creating support ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def log_customer_feedback(email_id: str, feedback: str):
    """Mock function to simulate logging customer feedback"""
    logger.info(f"Logging feedback for email {email_id}")
    # In real implementation: integrate with feedback system


def run_demonstration():
    """Run a demonstration of the complete system."""
    # Initialize the system
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)

    # Process all sample emails
    results = []
    for email in sample_emails:
        logger.info(f"\nProcessing email {email['id']}...")
        result = automation_system.process_email(email)
        results.append(result)

    # Create a summary DataFrame
    df = pd.DataFrame(results)
    print("\nProcessing Summary:")
    print(df[["email_id", "success", "classification", "response_sent"]])

    return df


# Example usage:
if __name__ == "__main__":
    results_df = run_demonstration()
