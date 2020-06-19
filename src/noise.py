# BassieRacing - Noise
# Based on: https://gist.github.com/healthonrails/a1afaa26980ecb599f21d750fcb0f446
# Which is based on: https://mrl.nyu.edu/~perlin/noise/

import math

class Noise:
    def __init__(self):
        self.permutation = [151, 160, 137, 91, 90, 15,
                            131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36,
                            103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23,
                            190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94,
                            252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
                            88, 237, 149, 56, 87, 174, 20, 125, 136, 171,
                            168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166,
                            77, 146, 158, 231, 83, 111, 229, 122, 60, 211,
                            133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244,
                            102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73,
                            209, 76, 132, 187, 208, 89, 18, 169, 200, 196,
                            135, 130, 116, 188, 159, 86, 164, 100, 109, 198,
                            173, 186, 3, 64, 52, 217, 226, 250, 124, 123,
                            5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207,
                            206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42,
                            223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163,
                            70, 221, 153, 101, 155, 167, 43, 172, 9,
                            129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224,
                            232, 178, 185, 112, 104, 218, 246, 97, 228,
                            251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162,
                            241, 81, 51, 145, 235, 249, 14, 239, 107,
                            49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204,
                            176, 115, 121, 50, 45, 127, 4, 150, 254,
                            138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243,
                            141, 128, 195, 78, 66, 215, 61, 156, 180]

        self.p = [self.permutation[i] for i in range(256)]
        self.p += self.p

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def noise(self, x, y, z):
        # Find unit cube that contains point.
        X = int(math.floor(x) & 255)
        Y = int(math.floor(y) & 255)
        Z = int(math.floor(z) & 255)

        # Find relative X, Y, Z
        # of point in CUBE.
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)

        # compute fade curves
        # for each of X, Y, Z

        u = self.fade(x)
        v = self.fade(y)
        w = self.fade(z)

        # Hash coordinates of the 8 cube corners
        A = self.p[X] + Y
        AA = self.p[A] + Z
        AB = self.p[A+1] + Z

        B = self.p[X+1] + Y
        BA = self.p[B] + Z

        BB = self.p[B + 1] + Z

        # And add bleneded results from 8 corners of cube

        return self.lerp(w, self.lerp(v, self.lerp(u, self.grad(self.p[AA], x, y, z),
                                                   self.grad(self.p[BA], x-1, y, z)),
                                      self.lerp(u, self.grad(self.p[AB], x, y-1, z),
                                                self.grad(self.p[BB], x-1, y-1, z))),
                         self.lerp(v, self.lerp(u, self.grad(self.p[AA+1], x, y, z-1),
                                                self.grad(self.p[BA+1], x-1, y, z-1)),
                                   self.lerp(u, self.grad(self.p[AB+1], x, y-1, z-1),
                                             self.grad(self.p[BB+1], x-1, y-1, z-1))))

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def grad(self, hash, x, y, z):
        h = hash & 15
        u = x if h < 8 else y
        if h < 4:
            v = y
        elif h == 12 or h == 14:
            v = x
        else:
            v = z

        res = u if (h & 1) == 0 else -u
        res += v if (h & 2) == 0 else -v
        return res
