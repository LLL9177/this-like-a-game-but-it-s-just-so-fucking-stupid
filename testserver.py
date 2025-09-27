from flask import Flask, request

app = Flask(__name__)

def is_answer_correct(answer: str) -> bool:
    if not answer:
        return False

    normalized = answer.lower().replace(" ", "")
    # valid letters sequence for Up-Left-Down-Right
    if normalized == "uldr":
        return True

    # compress word sequences
    seq = re.sub(r"[^a-z]", "", normalized)
    for word, ch in [("up","u"),("down","d"),("left","l"),("right","r")]:
        seq = seq.replace(word, ch)
    return seq == "uldr"

@app.route("/", methods=['POST'])
def index():
    if is_answer_correct(request.form.get("answer")):
        return "Some github link for animation!"
    
    return "Answer is incorrect :("

if __name__ == '__main__':
    app.run(port="8000")