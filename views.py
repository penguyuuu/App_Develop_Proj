from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import shelve

views = Blueprint('views', __name__)

def get_faqs():
    with shelve.open('faqs.db') as db:
        return db.get('faqs', [])

def save_faqs(faqs):
    with shelve.open('faqs.db') as db:
        db['faqs'] = faqs

@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        faqs = get_faqs()
        faqs.append({'question': question, 'answer': answer, 'likes': 0, 'reactions': []})
        save_faqs(faqs)
        return redirect(url_for('views.index'))

    faqs = get_faqs()
    return render_template('index.html', faqs=faqs)

@views.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_question(index):
    faqs = get_faqs()
    if request.method == 'POST':
        faqs[index]['question'] = request.form['question']
        faqs[index]['answer'] = request.form['answer']
        save_faqs(faqs)
        return redirect(url_for('views.index'))
    return render_template('edit_question.html', faq=faqs[index], index=index)

@views.route('/delete/<int:index>')
def delete_question(index):
    faqs = get_faqs()
    if 0 <= index < len(faqs):
        del faqs[index]
        save_faqs(faqs)
    return redirect(url_for('views.index'))

@views.route('/like/<int:index>', methods=['POST'])
def like_question(index):
    faqs = get_faqs()
    if 0 <= index < len(faqs):
        faqs[index]['likes'] += 1
        save_faqs(faqs)
        return jsonify({"likes": faqs[index]['likes']})
    return jsonify({"error": "Not Found"}), 404

@views.route('/react/<int:index>', methods=['POST'])
def react_to_question(index):
    faqs = get_faqs()
    if 0 <= index < len(faqs):
        reaction = request.json.get('reaction')
        faqs[index]['reactions'].append(reaction)
        save_faqs(faqs)
        return jsonify({"message": "Reaction added!"})
    return jsonify({"error": "Not Found"}), 404
