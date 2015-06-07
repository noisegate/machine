import pololu.pololu as pololu
import time


if __name__ == '__main__':
    y = pololu.Pololu(pololu.Pins(enable=15, direction=11,step=13))
    #x = pololu.Pololu(pololu.Pins(enable=26, direction=21,step=20))    

    y.disable()
    #x.disable()

