# ZIT (Zooplankton Image Tool)

![Marine Example](assets/mari_comp.png)

Makes plankton photos look real good. 


CLI: 
```bash
# Using poetry
poetry run zit --input samples/limo.mp4 --composite

# If installed
zit --input samples/limo.mp4 --composite
```

## Installation

```bash
poetry install
```

## Plankton Grid

### 184368 Comparison
| Eps 5 | Eps 10 | Eps 15 | Eps 25 | Eps 50 |
| :---: | :---: | :---: | :---: | :---: |
| ![Eps 5](assets/184368_eps5.png) | ![Eps 10](assets/184368_eps10.png) | ![Eps 15](assets/184368_eps15.png) | ![Eps 25](assets/184368_eps25.png) | ![Eps 50](assets/184368_eps50.png) |

### 230717 Comparison
| Eps 5 | Eps 10 | Eps 15 | Eps 25 | Eps 50 |
| :---: | :---: | :---: | :---: | :---: |
| ![Eps 5](assets/230717_eps5.png) | ![Eps 10](assets/230717_eps10.png) | ![Eps 15](assets/230717_eps15.png) | ![Eps 25](assets/230717_eps25.png) | ![Eps 50](assets/230717_eps50.png) |

### 307555 Comparison
| Eps 5 | Eps 10 | Eps 15 | Eps 25 | Eps 50 |
| :---: | :---: | :---: | :---: | :---: |
| ![Eps 5](assets/307555_eps5.png) | ![Eps 10](assets/307555_eps10.png) | ![Eps 15](assets/307555_eps15.png) | ![Eps 25](assets/307555_eps25.png) | ![Eps 50](assets/307555_eps50.png) |

![Plankton Example](assets/composited.png)
![Lovely Example](assets/plankt_oct19.jpg)
![Lovely Example](assets/plankt_oct06.jpg)
![Line Example](assets/li.png)
![HMM](assets/hmm.jpg)

# Documentation

You will find the `composite_from_frames` method useful for creating composites of plankton locomotion.

***skip*** allows for selection of specific frames window

***interval*** deteermines the cadence of video screen captures, in seconds

***noise_delta*** is based on the average pixel of the overlay. If the overlayed pixel is itself noise, do not overlay it

***composite_epsilon*** is the difference between overlay and background threshold required to perform the overlay in composition
