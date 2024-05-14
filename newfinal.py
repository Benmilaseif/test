import streamlit as st
from PyPDF2 import PdfReader
from fuzzywuzzy import process, fuzz
import google.generativeai as genai
import os

# Set the title of the Streamlit app
st.title("PDF QA System")

# Initialize conversation history
conversation_history = []

# Human and AI agent logos (Unicode characters)
human_logo = "👤"
ai_agent_logo = "🤖"

# React to user input
prompt = st.text_input("Ask your question:")

if prompt:
    # Add current question to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Set the path to your Google service account key file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\DELL\\Desktop\\Chatbot\\End-To-End-Gemini-Project-main\\inf.json"

    # Load PDF file
    pdf_path = r"bot.pdf"

    # Load and process the PDF file
    def process_pdf(file_path):
        context = ""
        try:
            pdf_loader = PdfReader(file_path)
            for page_number, page in enumerate(pdf_loader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        context += page_text
                    else:
                        print(f"No text extracted from page {page_number + 1}.")
                except Exception as e:
                    print(f"Error extracting text from page {page_number + 1}: {e}")
            if not context:
                print("No text extracted from the PDF.")
            return context
        except Exception as e:
            print("Error loading PDF: " + str(e))
            return None

    # Extract answers from the PDF with fuzzy matching and a higher threshold
    def extract_answer_from_pdf(question, content):
        if content:
            question = question.strip().lower()
            content = content.lower()
            lines = content.split("\n")

            best_match, match_ratio = process.extractOne(question, lines, scorer=fuzz.token_sort_ratio)

            if match_ratio > 85:  # Higher threshold for better matches
                question_index = lines.index(best_match)
                answer = "\n".join(lines[question_index + 1 : question_index + 6]).strip()
                return answer
            else:
                return "I couldn't find an answer in the document. Please ask a different question."
        else:
            return "PDF content could not be processed."

    # Generate response from Google Gemini with additional context
    def get_gemini_response(question):
        genai.configure(api_key=os.getenv("AIzaSyCv4R3JDg43LHH9kGKhaRqDsvm5a7XEIrs"))
        model = genai.GenerativeModel("gemini-pro")

        # Add contextual hint to improve response accuracy
        query_with_hint = f"Can you help answer this question: {question}?"
        response = model.generate_content(query_with_hint)

        return response.text.strip() if response.text else "No answer found from Google Gemini."

    # Main function for the chatbot
    def answer_question(question):
        # Load PDF content and extract answer from it
        pdf_content = process_pdf(pdf_path)
        pdf_answer = extract_answer_from_pdf(question, pdf_content)

        if pdf_answer and "I couldn't find" not in pdf_answer:
            return pdf_answer
        else:
            # Get response from Google Gemini if no valid answer from the PDF
            gemini_response = get_gemini_response(question)
            return gemini_response

    # Example usage
    answer = answer_question(prompt)
    conversation_history.append({"role": "assistant", "content": answer})

# Display conversation history
for message in conversation_history:
    if message["role"] == "user":
        st.write(f"{human_logo} You: {message['content']}")
    else:
        st.write(f"{ai_agent_logo} Assistant: {message['content']}")
