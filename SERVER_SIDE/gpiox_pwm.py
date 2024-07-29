#!/usr/bin/python3
from os import system, path
import time
import sys, traceback

class PWM:

    def __init__(self, pin, max_pulse, min_pulse, period): # pulses and period must be in ms

        self.max_pulse, self.min_pulse, self.current_pulse, self.period = max_pulse, min_pulse, (max_pulse + min_pulse) / 2, period
        pins, a, pwmx = [12, 13, 14, 15, 18, 19], [0, 0, 0, 0, 3, 3], [0, 1, 2, 3, 2, 3]
        self.pin = None
        

        if pin not in pins:
            raise IOError("Pin provided is invalid, valid pins for PWM are: 12, 13, 14, 15, 18, 19.")
       
        else:
            self.pin=pin
            self.current_pwmx = pwmx[pins.index(self.pin)]
            system("/usr/bin/pinctrl set {} a{}".format(self.pin,a[pins.index(self.pin)]))

                
            # Exporting the pin
            if path.exists("/sys/class/pwm/pwmchip2/pwm"+str(self.current_pwmx)) is False:
                self.__writeToFile("/sys/class/pwm/pwmchip2/export", self.current_pwmx)
                """
                wait_period = 5
                start = time.monotonic()
                
                while wait_period > time.monotonic() - start and path.exists("/sys/class/pwm/pwmchip2/pwm" + str(self.current_pwmx)) is False:
                    print("test")
                """
                # FINISH IT AND REPLACE sleep()

                time.sleep(.2)

            #System files
            self.period_file, self.duty_cycle_file = open("/sys/class/pwm/pwmchip2/pwm"+ str(self.current_pwmx) + "/period", "w"), open("/sys/class/pwm/pwmchip2/pwm" + str(self.current_pwmx) + "/duty_cycle", "w")
            if self.period_file.closed or self.duty_cycle_file.closed:
                self.pin = None
                raise IOError("Unable to export the pin correctly.")

            
        # Applying the period and current pulse
        self.period_file.write(str(self.period * 1000 * 1000))
        self.period_file.flush()

        self.duty_cycle_file.write(str(int(self.current_pulse * 1000 * 1000)))
        self.duty_cycle_file.flush()
    
    def __exit__(self):
        self.__del__()

    def __exit(self, signum, frame):
        self.__del__()
    
    def __del__(self):
        if self.pin is not None:
            # Closing Files
            if not self.duty_cycle_file.closed:
                time.sleep(1)
                self.duty_cycle_file.close()
            if not self.period_file.closed:
                self.period_file.close()
        try:
            # Unexporting the PWM pin
            self.__writeToFile("/sys/class/pwm/pwmchip2/unexport", self.current_pwmx)

            # Disabling PWM from the pin
            self.__writeToFile("/usr/bin/pinctrl set {} no", self.pin)
        except:
            pass 

    def __CheckEnabled(self):
        result = None
        with open("/sys/class/pwm/pwmchip2/pwm{}/enable".format(self.current_pwmx), "r") as r:
            result = int(r.read())
            r.close()
        return result

    def __ExceptionHandler(self): #todo: WRITE FUNCTION TAHT HANDLES ALL ERRORS TO ENSURE THAT SERVOS STOP
        pass

    def __PrintError(self, error):
        RedErrMark = "\033[41m[!]\033[0m"
        print(RedErrMark + error)

    def __writeToFile(self, file, text):
        try:
            with open(file, "w") as f:
                f.write(str(text))
                f.close()
            return True
        except:
            return False

    

    # USER FUNCTION AREA
    #
    #
    #

    def start(self):
            self.__writeToFile("/sys/class/pwm/pwmchip2/pwm{}/enable".format(int(self.current_pwmx)), 1)

    def stop(self): #RUNS ONCE
            self.__writeToFile("/sys/class/pwm/pwmchip2/pwm{}/enable".format(int(self.current_pwmx)), 0)
            self.__del__()
            

    def setPulse(self, pulse):
        state = self.__CheckEnabled()
        if state == 1:
            self.duty_cycle_file.write(str(int(pulse * 1000 * 1000))) # will return OSError if not in ms (and probably int too)
            self.duty_cycle_file.flush()
            self.current_pulse = pulse
        elif state == 0:
            self.__PrintError("Servo is not Enabled!")
        elif state == None:
            self.__PrintError("Unable to get PWM Status.")



    def current_pulse_func(self, from_file=False):
        try: # Returns current pulse in ms from either file or class variable.
            return int(open("/sys/class/pwm/pwmchip2/pwm{}/duty_cycle".format(self.pwmx[self.pinIdx]), "r").read()) / (1000 * 1000) if from_file else self.current_pulse
        except TypeError or ValueError: # If duty_cycle contains no value, then current_pulse() will return nothing
            return None




