import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class Stop(Node):

    def __init__(self):
        super().__init__('Stop')
        # -- Realiza as inscrições nos tópicos dos sensores
        self.subscription = self.create_subscription(LaserScan, '/robot/lidar', self.lidar_callback, 1)
        self.subscription # para previnir o "warning" de variável sem uso
        # -- Definição do Publisher das velocidades
        self.velPub = self.create_publisher(Twist, '/robot/cmd_vel', 1)
        timer_period = 3.333*1e-3  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        # -- Inicialização das variáveis
        self.laser_scan_data = LaserScan()
        self.encoder_data = Twist()
        self.start_flag = False


    def timer_callback(self):

        if(False): # Controlador
            # Obtém as menores leituras de distância dos lados esquerdo e direito
            distances = np.array(self.laser_scan_data.ranges)
            angles = np.linspace(self.laser_scan_data.angle_min, self.laser_scan_data.angle_max, len(distances))
            idc = (np.where(distances > 0))
            angles = angles[idc]
            distances = distances[idc]
            # Selecionado apenas as medidas frontais
            idc = (np.where(np.cos(angles-(np.pi/2.0)) < 0))
            angles = angles[idc]
            distances = distances[idc]
            # Determinação das menores distâncias de cada lado
            indices = np.where(np.sin(angles-(np.pi/2.0)) > 0)
            dL = np.min(distances[indices])/1000.0
            indices = np.where(np.sin(angles-(np.pi/2.0)) < 0)
            dR = np.min(distances[indices])/1000.0
            # Cálculos das velocidades com correção para desvio de obstáculo
            VL = 1.0
            VR = 1.0
            if dR<0.8:
                VL = 1.0 - 1.0*(1-np.tanh((dR-0.25)*5))
            if dL<0.8:
                VR = 1.0 - 0.5*(1-np.tanh((dL-0.25)*5))

            # Log
            self.get_logger().info(f'DistLeft: {dL:.2f} | DistRight: {dR:.2f}')
            self.get_logger().info(f'VelLeft: {VL:.2f} | VelRight: {VR:.2f}')

            VL = 0.0
            VR = 0.0
            # Publica as velocidades
            d = Twist()
            d.angular.x = VL
            d.angular.y = VR
            self.velPub.publish(d)


        else:
            self.get_logger().info('Esperando receber a primeira mensagem')
            d = Twist()
            d.angular.x = 0.0
            d.angular.y = 0.0
            self.velPub.publish(d)
            # Log
            self.get_logger().info(f'VelLeft: {d.angular.x:.2f} | VelRight: {d.angular.y:.2f}')


    def lidar_callback(self, msg):
        self.start_flag = True
        self.laser_scan_data = msg
        self.get_logger().info('Atualizando dados')
        


def main(args=None):


    # Inicilaização
    rclpy.init(args=args)

    # Criação de um nó instanciando uma classe do tipo "Node", por meio de "hierarquia"
    StopSub = Stop()

    # faz o spin do nó para habilitar recebimento de callbacks
    rclpy.spin(StopSub)

    # especificação de shutdown
    StopSub.destroy_node()
    rclpy.shutdown()
    


if __name__ == '__main__':
    main()
