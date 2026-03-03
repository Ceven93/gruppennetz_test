import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def calculate_metrics(df, students):
    results = {}

    for student in students:
        ratings = df[df["target"] == student]["rating"]

        if len(ratings) == 0:
            continue

        mean = ratings.mean()
        acc = (ratings == 6).sum() / (len(students)-1)
        rej = (ratings == 1).sum() / (len(students)-1)

        results[student] = {
            "mean": round(mean, 2),
            "acceptance": round(acc, 2),
            "rejection": round(rej, 2)
        }

    return results


def draw_sociogram(df, students, results):
    G = nx.DiGraph()

    for s in students:
        G.add_node(s)

    for _, row in df.iterrows():
        if row["nominated"] == 1:
            G.add_edge(row["respondent"], row["target"], weight=row["rating"])

    pos = nx.spring_layout(G, seed=42)

    indegree = G.in_degree()
    sizes = [800 + indegree[s]*400 for s in students]

    colors = []
    for s in students:
        m = results[s]["mean"]
        if 1 <= m <= 2:
            colors.append("orange")
        elif 3 <= m <= 4:
            colors.append("yellow")
        else:
            colors.append("green")

    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, edgecolors="black")
    nx.draw_networkx_labels(G, pos)

    for u, v, d in G.edges(data=True):
        style = "dashed" if d["weight"] < 4 else "solid"
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=2, style=style,
                               arrows=True, arrowsize=30, arrowstyle='-|>')

    plt.title("Soziogramm")
    return plt