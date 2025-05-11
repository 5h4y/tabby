from flask import Flask, render_template, send_from_directory, request
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../static')
TAB_DIR = os.environ.get("TABBY_TAB_DIR", "./tabs")
TAB_DIR = os.path.abspath(TAB_DIR)  # <— ensures absolute path
print(f"TAB_DIR resolved to: {TAB_DIR}")

def load_instruments():
    instruments = []
    for instrument_name in sorted(os.listdir(TAB_DIR)):
        instrument_path = os.path.join(TAB_DIR, instrument_name)
        if os.path.isdir(instrument_path):
            artists = []
            for artist_name in sorted(os.listdir(instrument_path)):
                artist_path = os.path.join(instrument_path, artist_name)
                if os.path.isdir(artist_path):
                    files = [f for f in os.listdir(artist_path) if f.endswith(".txt")]
                    artists.append({
                        "name": artist_name,
                        "files": files  # ensure nested files populate correctly
                    })
            instruments.append({
                "name": instrument_name,
                "artists": artists
            })
    return instruments


instruments = load_instruments()

def transpose_chord(chord, steps):
    semitones = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    match = re.match(r'^([A-G])(b|#)?(.*)$', chord)
    if not match:
        return chord  # not a recognized chord

    root, accidental, suffix = match.groups()
    accidental = accidental or ''
    suffix = suffix or ''

    note = root + accidental
    if note not in semitones:
        return chord  # skip invalid notes

    index = semitones.index(note)
    new_index = (index + steps) % 12
    return semitones[new_index] + suffix

def highlight_chords_in_line(line):
    def replacer(match):
        chord = match.group(0)
        return f'<span class="chord" data-chord="{chord}">{chord}</span>'
    
    chord_pattern = r'\b[A-G](#|b)?(m|maj7|maj|min|dim|aug|sus2|sus4|m7|7|6|9|11|13)?(#\d+|b\d+)?\b'
    return re.sub(chord_pattern, replacer, line)

@app.route("/")
def index():
    instruments = []

    print(f"[DEBUG] Root TAB_DIR: {TAB_DIR}")
    for instrument_name in sorted(os.listdir(TAB_DIR)):
        instrument_path = os.path.join(TAB_DIR, instrument_name)
        if not os.path.isdir(instrument_path):
            continue

        print(f"[DEBUG] Checking instrument: {instrument_name}")
        artists = []
        for artist_name in sorted(os.listdir(instrument_path)):
            artist_path = os.path.join(instrument_path, artist_name)
            if os.path.isdir(artist_path):
                files = [f for f in os.listdir(artist_path) if f.endswith(".txt")]
                if files:
                    artists.append({
                        "name": artist_name,
                        "files": sorted(files)
                    })
        if artists:
            instruments.append({
                "name": instrument_name,
                "artists": artists
            })

    print(f"[DEBUG] Instruments found: {instruments}")
    return render_template("index.html", instruments=instruments)

@app.route("/view/<instrument>/<artist>/<filename>")
def view_file(instrument, artist, filename):
    path = os.path.join(TAB_DIR, instrument, artist, filename)
    if not os.path.isfile(path):
        abort(404)

    with open(path, "r") as f:
        content = f.read()

    steps = int(request.args.get('transpose', 0))

    if steps != 0:
       content_lines = []
       for line in content.splitlines():
           words = line.split()
           transposed_line = " ".join(transpose_chord(word, steps) for word in words)
           content_lines.append(transposed_line)
    else:
       content_lines = content.splitlines()

    # apply chord highlighting
    highlighted_lines = [highlight_chords_in_line(line) for line in content_lines]
    content = "\n".join(highlighted_lines)

    def extract_chords_from_line(line):
       chord_pattern = r'\b[A-G](#|b)?(m|maj7|maj|min|dim|aug|sus2|sus4|m7|7|6|9|11|13)?(#\d+|b\d+)?\b'
       return re.findall(chord_pattern, line)

    unique_chords = set()
    for line in content_lines:
        words = line.split()
        for word in words:
            if re.match(r'^[A-G](#|b)?(m|maj7|maj|min|dim|aug|sus2|sus4|m7|7|6|9|11|13)?(#\d+|b\d+)?$', word):
                unique_chords.add(word)

    # sort chords
    sorted_chords = sorted(unique_chords)

    # render processed content
    return render_template(
        "view.html",
        filename=filename,
        content=content,
        instrument=instrument,
        artist=artist,
        transpose=steps,
	chords=sorted_chords
    )

# auto-populate instrument pages
@app.route("/instrument/<instrument_name>")
def instrument_page(instrument_name):
    instrument = next((i for i in instruments if i["name"] == instrument_name), None)
    if not instrument:
        abort(404)
    return render_template("instrument.html", instrument=instrument)

# auto-populate chord directory
@app.route("/chords")
def list_chords():
    chord_dir = os.path.join("static", "chords")
    files = sorted(f for f in os.listdir(chord_dir) if f.endswith(".svg"))
    return render_template("chords.html", chords=files)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
