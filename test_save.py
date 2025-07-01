from rag_system import save_correction

# Simulate saving a correction
save_correction(
    question="What is covered under preventive care?",
    original="Wrong answer.",
    corrected="Corrected by reviewer.",
    reviewer="Admin"
)