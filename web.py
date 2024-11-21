from flask import Flask, render_template, jsonify, request
from rdflib import Graph, Namespace

app = Flask(__name__)

def inGraph(query):
    g = Graph()
    g.parse("/app/neurov.owl", format="xml")

    querys = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX db: <http://www.semanticweb.org/artyo/ontologies/2024/9/untitled-ontology-5#>
    """
    query = querys + "\n" + query
    results = g.query(query)
    return results

@app.route("/")
def is_main():
    return render_template("main.html")

@app.route("/v1")
def view1():
    results = inGraph('''SELECT ?HistoryModel ?a ?b
WHERE {
?HistoryModel db:name_history ?a. FILTER(?a = 'Модель1'^^xsd:string)
?HistoryModel db:history_version ?b
} ''')

    classes = []
    for row in results:

        classes.append({
            "HistoryModel": str(row["HistoryModel"]),
            "a": str(row["a"]),
            "b": str(row["b"]),
        })

    return render_template("select1.html", classes=classes)


@app.route("/v2")
def view2():
    results = inGraph('''SELECT ?neuro ?nn ?model ?iter ?nt
WHERE {
?iter db:IterHasModel ?model.
?model db:hasNeuro ?neuro.
?neuro db:name_neuro ?nn. FILTER(?nn = 'Сверточная нейронная сеть'^^xsd:string)
?iter db:hasObjects ?obj.
?obj db:hasType ?type.
?type db:name_type ?nt.
}''')

    classes = []
    for row in results:

        classes.append({
            "neuro": str(row["neuro"]),
            "nn": str(row["nn"]),
            "model": str(row["model"]),
            "iter": str(row["iter"]),
            "nt": str(row["nt"]),
        })

    return render_template("select2.html", classes=classes)


@app.route("/v3")
def view3():
    results = inGraph('''SELECT ?model (COUNT(?history) as ?count) where {?history db:HistoryHasModel ?model}
group by ?model
''')

    classes = []
    for row in results:

        classes.append({
            "model": str(row["model"]),
            "count": str(row["count"]),
        })

    return render_template("select3.html", classes=classes)


@app.route("/v4")
def view4():
    results = inGraph('''SELECT ?no ?dco
WHERE {
?obj db:date_create_object ?dco. FILTER(?dco > '2024-10-23T00:00:00'^^xsd:dateTime)
?obj db:name_object ?no
}
''')

    classes = []
    for row in results:

        classes.append({
            "no": str(row["no"]),
            "dco": str(row["dco"]),
        })

    return render_template("select4.html", classes=classes)


@app.route("/v5")
def view5():
    results = inGraph('''SELECT ?model ?nm ?his ?dch
WHERE {
?model db:name_model ?nm.  FILTER(?nm = 'Модель1'^^xsd:string)
?his db:HistoryHasModel ?model.
?his db:date_create_history ?dch.
}
order by desc(?dch)
''')

    classes = []
    for row in results:

        classes.append({
            "model": str(row["model"]),
            "nm": str(row["nm"]),
            "his": str(row["his"]),
            "dch": str(row["dch"]),
        })

    return render_template("select5.html", classes=classes)


@app.route("/v6")
def view6():
    results = inGraph('''SELECT ?mn ?tn ?nn
WHERE {
?model db:hasTask ?task.
?model db:hasNeuro ?neuro.
?model db:name_model ?mn.
?task db:name_task ?tn.
?neuro db:name_neuro ?nn.
}
''')

    classes = []
    for row in results:

        classes.append({
            "mn": str(row["mn"]),
            "tn": str(row["tn"]),
            "nn": str(row["nn"]),
        })

    return render_template("select6.html", classes=classes)


@app.route("/v7")
def view7():
    results = inGraph('''SELECT ?model (COUNT(?obj) as ?count) where {?iter db:IterHasModel ?model.
?iter db:hasObjects ?obj.
                      }
group by ?model''')

    classes = []
    for row in results:
        classes.append({
            "model": str(row["model"]),
            "count": str(row["count"]),
        })

    return render_template("select7.html", classes=classes)


@app.route("/v8")
def view8():
    results = inGraph('''SELECT ?mn ?cl
WHERE {
?model db:name_model ?mn.
?model db:count_layers ?cl. FILTER(?cl > 9)
}
ORDER BY DESC(?cl)''')

    classes = []
    for row in results:
        classes.append({
            "mn": str(row["mn"]),
            "cl": str(row["cl"]),
        })

    return render_template("select8.html", classes=classes)


@app.route("/v9")
def view9():
    results = inGraph('''SELECT ?mn ?d
WHERE {
?iter db:IterHasModel ?model.
?model db:name_model ?mn.
?iter db:date_create_iter ?d.
}
ORDER BY DESC(?d)''')

    classes = []
    for row in results:
        classes.append({
            "mn": str(row["mn"]),
            "d": str(row["d"]),
        })

    return render_template("select9.html", classes=classes)


@app.route('/v10')
def view10():
    results = inGraph('''SELECT ?neuro (COUNT(?model) as ?count) where {?model db:hasNeuro ?neuro}
group by ?neuro''')
    classes = []
    for row in results:

        classes.append({
            "neuro": str(row["neuro"]),
            "count": str(row["count"]),
        })

    return render_template("select10.html", classes=classes)


@app.route("/ask", methods=["POST"])
def ask_query():
    data = request.get_json()
    model_name = data.get("model_name")

    # Формируем запрос ASK
    query = f'''
    ASK {{
        ?model db:name_model "{model_name}"^^xsd:string.
    }}
    '''
    result = inGraph(query)  # Выполняем запрос с помощью inGraph
    is_present = bool(result.askAnswer)  # Проверяем результат (True/False)

    # Возвращаем результат в формате JSON
    return jsonify({"model_name": model_name, "is_present": is_present})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
