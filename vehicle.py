class Vehicle:
    def __init__(self, id): # , v_c, v_w, v_l, t_id
        self.id = id
        self.timestamp = []
        self.utm_x = []
        self.utm_y = []
        self.v = []
        self.tipo_ruta = 0
        #self.utm_angle = []
        #self.acc = []
        #self.acc_lat = []
        #self.acc_tan = []
        self.v_class = ""
        #self.v_width = v_w
        #self.v_length = v_l
        #self.trailer_id = t_id

    #def display(self):
    #   