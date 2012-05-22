class atlas_loc:
    Name = "Atlas Location"
    def __init__(self, condition, subject, run, x, y, z, std_x, std_y, std_z, atlas_percentages):
        self.condition = condition
        self.subject = subject
        self.run = run
        self.x = x
        self.y = y
        self.z = z
        self.std_x = std_x
        self.std_y = std_y
        self.std_z = std_z
        self.atlas_percentages = atlas_percentages

