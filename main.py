import networkx as nx
import matplotlib.pyplot as plt


# ----------------------------
# Kinder eingeben
# ----------------------------
def kinder_eingeben():
    kinder = []
    print("Gib die Namen der Kinder ein.")
    print("Leere Eingabe beendet die Eingabe.\n")

    while True:
        name = input("Name: ")
        if name == "":
            break
        kinder.append(name)

    return kinder


# ----------------------------
# Fragebogen
# ----------------------------
def fragebogen_durchfuehren(kinder):
    daten = {}

    print("\n--- Fragebogen startet ---\n")

    for kind in kinder:
        print(f"\nJetzt beantwortet {kind} den Fragebogen.")

        print("Mit welchen Kindern spielst du oft?")
        print("Mehrere Namen mit Komma trennen (z.B. Anna,Ben)")
        eingabe = input("Nennungen: ")

        if eingabe == "":
            nennungen = []
        else:
            nennungen = [name.strip() for name in eingabe.split(",")]

        bewertungen = {}

        for anderes_kind in kinder:
            if anderes_kind != kind:
                while True:
                    try:
                        wert = int(input(f"Wie gerne spielst du mit {anderes_kind}? (0–6): "))
                        if 0 <= wert <= 6:
                            bewertungen[anderes_kind] = wert
                            break
                        else:
                            print("Bitte Zahl zwischen 0–6 eingeben.")
                    except:
                        print("Bitte gültige Zahl eingeben.")

        daten[kind] = {
            "nennungen": nennungen,
            "bewertungen": bewertungen
        }

    return daten


# ----------------------------
# Kennwerte berechnen
# ----------------------------
def auswertung_berechnen(kinder, daten):
    ergebnisse = {}
    n = len(kinder)

    for ziel in kinder:
        bewertungen_fuer_kind = []

        for quelle in kinder:
            if quelle != ziel:
                wert = daten[quelle]["bewertungen"][ziel]
                bewertungen_fuer_kind.append(wert)

        mittelwert = sum(bewertungen_fuer_kind) / (n - 1)
        akzeptanz = bewertungen_fuer_kind.count(6) / (n - 1)
        ablehnung = bewertungen_fuer_kind.count(1) / (n - 1)

        ergebnisse[ziel] = {
            "mittelwert": round(mittelwert, 2),
            "akzeptanz": round(akzeptanz, 2),
            "ablehnung": round(ablehnung, 2)
        }

    return ergebnisse


# ----------------------------
# Soziogramm zeichnen
# ----------------------------
def soziogramm_zeichnen(kinder, daten, ergebnisse):
    import matplotlib.patches as mpatches

    G = nx.DiGraph()

    for kind in kinder:
        G.add_node(kind)

    # Kanten (nur Nominationen)
    for quelle in kinder:
        for ziel in kinder:
            if ziel != quelle:
                if ziel in daten[quelle]["nennungen"]:
                    gewicht = daten[quelle]["bewertungen"][ziel]
                    G.add_edge(quelle, ziel, weight=gewicht)

    pos = nx.spring_layout(G, seed=42)

    # ---------------------------
    # Zentralität (In-Degree)
    # ---------------------------
    indegree = G.in_degree()
    node_sizes = [800 + indegree[k]*400 for k in kinder]

    # ---------------------------
    # Knotenfarben (diskret)
    # ---------------------------
    node_colors = []
    for kind in kinder:
        m = ergebnisse[kind]["mittelwert"]

        if 1 <= m <= 2:
            node_colors.append("orange")
        elif 3 <= m <= 4:
            node_colors.append("yellow")
        elif 5 <= m <= 6:
            node_colors.append("green")
        else:
            node_colors.append("lightgrey")

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        edgecolors="black"
    )

    nx.draw_networkx_labels(G, pos)

    # ---------------------------
    # Kanten
    # ---------------------------
    for u, v, data in G.edges(data=True):
        gewicht = data["weight"]

        style = "dashed" if gewicht < 4 else "solid"

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(u, v)],
            width=2,
            style=style,
            arrows=True,
            arrowsize=30,
            arrowstyle='-|>'
        )

    # ---------------------------
    # Legende
    # ---------------------------
    orange_patch = mpatches.Patch(color='orange', label='MW 1–2')
    yellow_patch = mpatches.Patch(color='yellow', label='MW 3–4')
    green_patch = mpatches.Patch(color='green', label='MW 5–6')

    plt.legend(handles=[orange_patch, yellow_patch, green_patch])
    plt.title("Soziogramm\nGrösse = In-Degree | gestrichelt = Bewertung < 4")
    plt.show()