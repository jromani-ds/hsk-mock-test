"""HSK Constants and Standards"""

# HSK 3.0 Passing thresholds (Generalized for mock# Passing Score
PASSING_SCORE_PERCENTAGE = 60

# Question Types
QUESTION_TYPE_MC = "MC"
QUESTION_TYPE_FIB = "FIB"
QUESTION_TYPE_WRITING = "WRITING"

# HSK 3.0 Exam Structure (Approximate Question Counts)
# Based on official guidelines (Listening + Reading + Writing)
# Note: Listening is simulated via Text cues or Reading comprehension in this CLI version
HSK_EXAM_STRUCTURE = {
    1: 40,  # ~40 items
    2: 60,  # ~60 items
    3: 80,  # 80 items
    4: 100, # 100 items
    5: 100, # 100 items
    6: 101, # 101 items
    7: 98,  # Advanced Band (Est.)
    8: 98,
    9: 98
}

# HSK Level Descriptions
LEVEL_DESCRIPTIONS = {
    1: "Beginner - Understand and use simple Chinese words and phrases",
    2: "Beginner - Communicate in simple and routine tasks directly",
    3: "Beginner - Complete basic communicative tasks in life/study",
    4: "Intermediate - Discuss a relatively wide range of topics",
    5: "Intermediate - Read Chinese newspapers and watch movies",
    6: "Intermediate - Easily comprehend written and spoken information",
    7: "Advanced - Near-native proficiency in all domains",
    8: "Advanced - Near-native proficiency in all domains",
    9: "Advanced - Near-native proficiency in all domains",
}


# Interaction Messages
MSG_CORRECT = "Correct."
MSG_INCORRECT = "Incorrect. The answer was: {answer}"
MSG_PASS = "Excellent. You are Exam Ready for Level {level}."
MSG_FAIL = "Insufficient. Focused practice required."
MSG_GRAMMAR_AUDIT = "\nGrammar Audit:\n{audit}"
MSG_CHALLENGE = "\nChallenge Question (Level {level}):"
