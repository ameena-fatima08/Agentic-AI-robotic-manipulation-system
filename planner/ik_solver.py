import math

class IKSolver:

    def __init__(self):
        # 🔥 Adjust based on your real arm (in cm)
        self.L1 = 6   # base to shoulder
        self.L2 = 13.5  # shoulder to elbow
        self.L3 = 10   # elbow to wrist

    def solve(self, x, y, z):

        try:
            # -----------------------------
            # 1️⃣ BASE ROTATION
            # -----------------------------
            theta1 = math.degrees(math.atan2(x, y))

            # -----------------------------
            # 2️⃣ PLANAR DISTANCE
            # -----------------------------
            r = math.sqrt(x**2 + y**2)
            z = z - self.L1  # adjust base height

            # distance to target
            D = math.sqrt(r**2 + z**2)

            if D > (self.L2 + self.L3):
                print(" Target out of reach")
                return None
            
            if D < abs(self.L2 - self.L3):
                print(" Target too close")
                return None

            # -----------------------------
            # 3️⃣ ELBOW (LAW OF COSINES)
            # -----------------------------
            cos_theta3 = (D**2 - self.L2**2 - self.L3**2) / (2 * self.L2 * self.L3)

            cos_theta3 = max(-1.0, min(1.0, cos_theta3))

            theta3 = math.degrees(math.acos(cos_theta3))

            # -----------------------------
            # 4️⃣ SHOULDER
            # -----------------------------
            alpha = math.atan2(z, r)
            beta = math.acos((D**2 + self.L2**2 - self.L3**2) / (2 * D * self.L2))

            theta2 = math.degrees(alpha + beta)

            # -----------------------------
            # 5️⃣ WRIST PITCH
            # -----------------------------
            theta4 = 180 - (theta2 + theta3)

            # -----------------------------
            # 6️⃣ WRIST ROTATE
            # -----------------------------
            if x > 0:
                theta5 = 110
            else:
                theta5 = 70
            def clamp(val, min_v, max_v):
                return max(min_v, min(max_v, val))
                
            return {
                "servo1": clamp(int(90 + theta1), 10, 170),
                "servo2": clamp(int(theta2), 20, 160),
                "servo3": clamp(int(theta3), 20, 160),
                "servo4": clamp(int(theta4), 10, 170),
                "servo5": clamp(int(theta5), 0, 180)
            }
        except Exception as e:
            print(" IK Error:", e)
            return None