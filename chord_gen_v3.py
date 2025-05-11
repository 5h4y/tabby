import matplotlib.pyplot as plt
import os
import csv

def normalize_frets(frets):
    return [f + 1 if f > 0 else f for f in frets]

def parse_csv_row(row):
    name = row["name"]
    frets = list(map(int, row["frets"].split(",")))
    fingers = list(map(int, row["fingers"].split(",")))
    return name, normalize_frets(frets), fingers

def generate_chord_diagram(chord_name, frets, fingers=None, save_path="static/chords"):
    os.makedirs(save_path, exist_ok=True)

    fig, ax = plt.subplots(figsize=(2, 3))
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(0, 5.5)
    ax.invert_yaxis()

    # draw vertical strings
    for x in range(6):
        ax.plot([x, x], [1, 5], color="black", linewidth=1.5)

    # draw nut line at the top
    ax.plot([-0.5, 5.5], [1, 1], color="black", linewidth=4)

    # draw horizontal frets
    for y in range(2, 6):
        ax.plot([-0.5, 5.5], [y, y], color="black", linewidth=1.5)

    # draw finger positions and numbers
    for string, fret in enumerate(frets):
        if fret > 0:
            visual_fret = fret - 0.5
            ax.plot(string, visual_fret, 'o', color="#0077cc", markersize=12)

            if fingers and len(fingers) > string and fingers[string] > 0:
                ax.text(
                    string, visual_fret, str(fingers[string]),
                    ha="center", va="center", color="white",
                    fontsize=9, fontweight="bold"
                )

    # open vs muted string indicators
    for string, fret in enumerate(frets):
        if fret == 0:
            ax.text(string, 0.6, "O", ha="center", va="center", fontsize=10, fontweight="bold")
        elif fret == -1:
            ax.text(string, 0.6, "X", ha="center", va="center", fontsize=10, fontweight="bold")

    # chord name
    ax.text(2.5, 0.3, chord_name, fontsize=14, ha="center", fontweight="bold")

    ax.axis('off')
    filename = os.path.join(save_path, f"{chord_name}.svg")
    plt.savefig(filename, bbox_inches='tight', format='svg')
    plt.close()
    print(f"Saved: {filename}")

def batch_generate_from_csv(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                name, frets, fingers = parse_csv_row(row)
                generate_chord_diagram(name, frets, fingers)
            except Exception as e:
                print(f"Error processing {row['name']}: {e}")

if __name__ == "__main__":
    batch_generate_from_csv("chords.csv")
