import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


# --------------------------------------------------
# METRIKEN BERECHNEN
# --------------------------------------------------

def calculate_metrics(df, students):

    n = len(students)
    results = {}

    for student in students:

        received = df[df["target"] == student]
        ratings = received["rating"].tolist()

        if ratings:
            mean_rating = round(sum(ratings) / len(ratings), 2)
            acceptance = round(ratings.count(6) / (n - 1), 2)
            rejection = round(ratings.count(1) / (n - 1), 2)
        else:
            mean_rating = 0
            acceptance = 0
            rejection = 0

        in_degree = len(df[(df["target"] == student) & (df["nominated"] == 1)])
        out_degree = len(df[(df["respondent"] == student) & (df["nominated"] == 1)])

        results[student] = {
            "Mittelwert": mean_rating,
            "Akzeptanz": acceptance,
            "Ablehnung": rejection,
            "In-Degree": in_degree,
            "Out-Degree": out_degree
        }

    return results


# --------------------------------------------------
# SOZIOGRAMM ZEICHNEN
# --------------------------------------------------

def draw_sociogram(df, students, results):

    G = nx.DiGraph()

    for s in students:
        G.add_node(s)

    # Kanten
    for _, row in df.iterrows():
        if row["nominated"] == 1:
            G.add_edge(row["respondent"], row["target"], rating=row["rating"])

    pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Knotengrösse = In-Degree
    node_sizes = [300 + results[s]["In-Degree"] * 200 for s in G.nodes()]

    # Farbe nach Mittelwert
    node_colors = []
    for s in G.nodes():
        mean = results[s]["Mittelwert"]
        if mean <= 2:
            node_colors.append("orange")
        elif mean <= 4:
            node_colors.append("yellow")
        else:
            node_colors.append("green")

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        ax=ax
    )

    nx.draw_networkx_labels(G, pos, ax=ax)

    # Kanten zeichnen
    for u, v, data in G.edges(data=True):

        rating = data["rating"]

        # gestrichelt bei Bewertung <4
        style = "dashed" if rating < 4 else "solid"

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(u, v)],
            arrowstyle="-|>",
            arrowsize=20,
            width=1.5,
            style=style,
            ax=ax
        )

    # Legende
    ax.scatter([], [], c="orange", s=300, label="Mittelwert 0–2")
    ax.scatter([], [], c="yellow", s=300, label="Mittelwert 3–4")
    ax.scatter([], [], c="green", s=300, label="Mittelwert 5–6")

    ax.legend()
    ax.set_title("Soziogramm")
    ax.axis("off")

    return fig