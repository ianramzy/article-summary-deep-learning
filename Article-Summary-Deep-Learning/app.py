from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import spacy
from spacy import displacy
from collections import Counter
import textacy.extract
import webbrowser

nlp = spacy.load('en_core_web_lg')

app = Flask(__name__)


@app.route('/')
def student():
    return render_template("input.html")

@app.route('/visualization')
def visualization():
    return render_template("visualization.html")


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        value = request.form.get('Name')
        print("Recieved: " + value)
        article = nlp(url_to_string(value))
        top_entities = findNER(article)
        facts = printFacts(top_entities, article)
        renderPicture(article)
        # visualization = renderPicture(article)
        return render_template("output.html", top_entities=top_entities, facts=facts)


if __name__ == '__main__':
    app.run(debug=True)


def url_to_string(url):
    if not re.match('(?:http|ftp|https)://', url):
        url = 'http://{}'.format(url)
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    for script in soup(["script", "style", 'aside']):
        script.extract()
    return " ".join(re.split(r'[\n\t]+', soup.get_text()))


def findNER(article):
    entities = []
    for ent in article.ents:
        if ent.label_ in ["ORG", "PERSON", "NORP", "FAC", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART"]:
            entities.append(ent)
    no_dup_entities = [x.text for x in entities]
    top_entities = Counter(no_dup_entities).most_common(4)
    for i in range(len(top_entities)):
        top_entities[i] = top_entities[i][0]
    return top_entities


def printFacts(top_entities,  article):
    strStatements = []
    statements = textacy.extract.semistructured_statements(article, top_entities[0])
    print("Here are the things I know about " + top_entities[0] + ": ")
    for statement in statements:
        subject, verb, fact = statement
        # print(f"     - {fact}")
        strStatements.append(str(fact).split(".")[0])  # truncate at .
    # print(" ")
    print(strStatements)
    return strStatements

def renderPicture(article):
    colors = {"ORG": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}
    options = {"ents": ["ORG", "PERSON", "NORP", "FAC", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART"],
               "bg": "#white", "color": "black", "font": "Montserrat"}

    # displacy.render(article, jupyter=False, style='ent', options=options)
    f = open("templates/visualization.html", "w")
    f.write(displacy.render(article, style="ent", page=True, options=options))
    f.close()




