from simulator import Simulator

from tango import AttrWriteType
from tango.server import Device, attribute, command, run
from constants import *


class PaintTank(Device):
    """
    Tango device server implementation representing a single paint tank
    """
    def init_device(self):
        super().init_device()
        print("Initializing class %s for device %s" % (self.__class__.__name__, self.get_name()))
        # extract the tank name from the full device name, e.g. "epfl/station1/cyan" -> "cyan"
        tank_name = self.get_name().split('/')[-1]
        # get a reference to the simulated tank
        self.tank = simulator.get_paint_tank_by_name(tank_name)
        if not self.tank:
            raise Exception(
                "Error: Can't find matching paint tank in the simulator with given name = %s" % self.get_name())

    @command(dtype_out=float)
    def Flush(self):
        """
        command to flush all paint
        """
        self.tank.flush()
        self.info_stream(f"PaintTank {self.get_name()} got flushed.")
        return self.tank.get_level()
   
    @attribute(dtype=float)
    def level(self):
        """
        get level attribute
        range: 0 to 1
        """
        return self.tank.get_level()

    @attribute(dtype=float)
    def flow(self):
        """
        get flow attribute
        """
        return self.tank.get_outflow()

    valve = attribute(label="valve", dtype=float,
                      access=AttrWriteType.READ_WRITE,
                      min_value=0.0, max_value=1.0, #in %, we can show the actual values in the GUI by multiplying
                      fget="get_valve", fset="set_valve")

    def set_valve(self, ratio):
        """
        set valve attribute
        :param ratio: 0 to 1
        """
        self.tank.set_valve(ratio)

    def get_valve(self):
        """
        get valve attribute (range: 0 to 1)
        """
        return self.tank.get_valve()

    @attribute(dtype=bool)
    def VHS(self):
        """
        see whether VHS is activated
        """
        return self.level() < VHS_LEVEL
    
    @attribute(dtype=bool)
    def HS(self):
        """
        see whether HS is activated
        """
        return self.level() < HS_LEVEL
    
    @attribute(dtype=bool)
    def LS(self):
        """
        see whether LS is activated
        """
        return self.level() > LS_LEVEL
    
    @attribute(dtype=bool)
    def VLS(self):
        """
        see whether VLS is activated
        """
        return self.level() > VSL_LEVEL
    

    @command(dtype_out=float)
    def fill(self):
        """
        command to fill up the tank with paint
        """
        self.tank.fill()
        self.info_stream(f"ColorTank {self.get_name()} got filled")

        return self.tank.get_level()
    
    @attribute(dtype=str)
    def color(self):
        """
        get color attribute (hex string)
        """
        return self.tank.get_color_rgb()  # grey
    
  
    
    LM = attribute(label="LM", dtype=float, #represents the speed of the motor (as a % of the max speed)
                   access=AttrWriteType.READ_WRITE,
                   min_value=0.0, max_value=1.0,
                   fget="get_LM", fset="set_LM")
    def get_LM(self):
        """
        get the current speed of the left motor (as % of the max motor speed)
        """
        return self.mixer.get_lm_speed()

    def set_LM(self, ratio):
        """
        set the current speed of the left motor (as % of the max motor speed)
        """
        self.mixer.set_lm_speed(ratio)

    RM = attribute(label="RM", dtype=float, #represents the speed of the motor (as a % of the max speed)
                   access=AttrWriteType.READ_WRITE,
                   min_value=0.0, max_value=1.0,
                   fget="get_RM", fset="set_RM")
    def get_RM(self):
        """
        get the current speed of the right motor (as % of the max motor speed)
        """
        return self.mixer.get_rm_speed()

    def set_RM(self, ratio):
        """
        set the current speed of the right motor (as % of the max motor speed)
        """
        self.mixer.set_rm_speed(ratio)
    

   

if __name__ == "__main__":
    # start the simulator as a background thread
    simulator = Simulator()
    simulator.start()

    # start the Tango device server (blocking call)
    run((PaintTank,))
