from PIL import Image


class Organisms:
    def get_organisms():
        survey = {
            "BACTERIA": {
                "Cyanobacteria": ["Chroococcales", "Oscillatoriales", "Nostocales"],
                "Prochlorobacteria": ["Prochlorales"],
                "Anoxyphotobacteria": {["Chromatiaceae", "Chlorobiaceae"]},
            },
            "EUCARYA": {"Glau"},
        }


def classify(img: Image) -> str:
    return "0"


if __name__ == "__main__":
    print(classify("f"))
