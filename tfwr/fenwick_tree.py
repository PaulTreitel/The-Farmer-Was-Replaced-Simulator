class FenwickTree:
    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height
        self.tree = [[0] * (width + 1) for _ in range(height + 1)]

    def add(self, x: int, y: int, delta: int) -> None:
        y += 1
        while y <= self.h:
            xx = x + 1
            while xx <= self.w:
                self.tree[y][xx] += delta
                xx += xx & -xx
            y += y & -y

    def prefix(self, x: int, y: int) -> int:
        total = 0
        while y > 0:
            xx = x
            while xx > 0:
                total += self.tree[y][xx]
                xx -= xx & -xx
            y -= y & -y
        return total

    def rect(self, x1, y1, x2, y2) -> int:
        """
        Inclusive-exclusive:
        [x1,x2) × [y1,y2)
        """
        return (
            self.prefix(x2, y2)
            - self.prefix(x1, y2)
            - self.prefix(x2, y1)
            + self.prefix(x1, y1)
        )
