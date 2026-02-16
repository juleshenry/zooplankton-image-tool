from PIL import Image


class Organisms:
    @staticmethod
    def get_organisms():
        survey = {
            "BACTERIA": {
                "Cyanobacteria": ["Chroococcales", "Oscillatoriales", "Nostocales"],
                "Prochlorobacteria": ["Prochlorales"],
                "Anoxyphotobacteria": {"Chromatiaceae", "Chlorobiaceae"},
            },
            "EUCARYA": {"Glau"},
        }
        return survey


def classify(img: Image.Image) -> str:
    return "0"


if __name__ == "__main__":
    # Test with a dummy image if needed
    print(classify(Image.new("RGB", (10, 10))))
