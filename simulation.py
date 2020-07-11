import random
RUNS=50                                 # Number of Runs
prob = 0.1                              # Probability of packet creation
W = 4                                   # Number of Channels
N = 8                                   # Number of Nodes
NO_OF_SLOTS = 1000000                   # Lots of time slots running every simulation
QUEUE_SIZE = 4                          # Maximum queue size
bufferFails = [0,0,0,0,0,0,0,0]         # Failed packet Counters due to full buffer
queues = [[None] * N] * N               # Tables with the queues of packages, one for each pair of transmitter receivers
slot = 0                                # Time Counter (timeslots)
# transmittedPackages = List of packages that have been successfully sent. listOfNodes = List of Nodes. 
# listOfChannels =  List of Channels, listOfNodesPerChannel = List the total number of channels each node uses.
transmittedPackages, listOfNodes, listOfChannels, listOfNodesPerChannel = ([] for i in range(4))
noOfPacketsGenerated = 0                # Counter for created packets
debug = False                           # debug test if it is true prints intermediate data

#Class Packet
class Packet:
    # ένας constructor
    def __init__(self, slotCreated, transmitter, receiver):
        self.slotCreated = slotCreated   # When exactly the packet created
        self.slotSent = 0                # When sent
        self.transmitter = transmitter   # From which Transmitter
        self.receiver = receiver         # To which Receiver

    # Packet delay Calculation
    def getDelay(self):
        return self.slotSent - self.slotCreated

    # Defines when it was sent
    def setSlotSent(self, s):
        self.slotSent = s

    # Formatted output for printing packet data
    def __str__(self):
        return "Time Slot:"+str(self.slotCreated)+" From:"+str(self.transmitter)+" To:"+et(self.receiver)+" Sent:"+str(self.slotSent)+" Delay:"+str(self.getDelay())

# Method for calculating the average packet delay
def calcAverageDelay(packet_list):
    sum_delay = 0
    for p in packet_list:
        sum_delay = sum_delay + p.getDelay()

    avg = sum_delay / len(packet_list)
    return avg

# Method for throughput calculation
def calcThroughPut():
    global transmittedPackages
    return len(transmittedPackages) / slot  # packages that arrived at their destination / time slots

# We define here which channels each node transmits
def setChannels():
    global listOfNodesPerChannel
    # In this system (System 3) all nodes transmit to all channels
    # Here we have: the list {{1,2,3,4,5,6,7,8}, {1,2,3,4,5,6,7,8}, {1,2,3,4 , 5,6,7,8}, {1,2,3,4,5,6,7,8}}
    for _ in range(0, W):
        l1 = []
        for j in range(0, N):
            l1.append(j + 1)
        listOfNodesPerChannel.append(l1)

# The algorithm for selecting channels without conflicts
def schedule(omega, a):
    trans = [0] * N               #  Empty Table Creation
    while len(omega) > 0:         # While in Ω we have data

        # Step2 we choose random channel K
        r1 = int(random.random() * len(omega))
        k = omega[r1]

        # Step3 we choose random node i from the total of Ak.
        r2 = int(random.random() * len(a[k - 1]))
        i = 0
        if len(a[k - 1]) > 0:
            i = a[k - 1][r2]

            # Step4 We put in array the channel k in node's i position.
            trans[i-1] = k

        # Step5 We remove the node from the list
        omega.pop(r1)
        for j in range(0, len(a)):
            a[j].remove( i )    # ACTUNG! check 

    if debug and slot==54:     # debugging, prints Array trans
        for i in range(0, 8):
            print(str(trans[i]) + " " , end =" ")
        print("")
    return trans

# Function that copies the channel table
def copyChannels():
    global listOfChannels
    result_list = []
    for i in listOfChannels:
        result_list.append(i)
    return result_list

# Entry Point
for run in range(1, RUNS + 1):                      # rerun of simulations
    prob = 0.1                                      # Probability of packet creation
    slot = 0
    transmittedPackages, listOfNodes, listOfChannels, listOfNodesPerChannel = ([] for i in range(4))
    noOfPacketsGenerated = 0
    for i in range(0, N):                           # Lists creation once for each pair of sender-recipient
        for j in range(0, N):                       # The L limit refers to all packets of a sender
            queues[i][j] = []
    prob=0.001+0.8*(run / RUNS)                     # range of probabilities eg: 0.1, 0.2, 0.3, 0.4 (depending on RUNS)
    # Defining the nodes total
    for i in range(0, N):
        listOfNodes.append(i+1)                     # Nodes list {1,2,3,4,5,6,7,8}
    for i in range(0, W):                           # Defining the channel total
        listOfChannels.append(i+1)                  # О— О»ОЇПѓП„О± П„П‰ОЅ ОєО±ОЅО±О»О№ПЋОЅ {1,2,3,4}
    setChannels()                                   # Defining the "sending" channels that each node will have
    for s in range(0, NO_OF_SLOTS):                 # Repeat the process for successive timeslots
        for i in range(0, N):                       # Create packages for each node independently
            r = random.random()                     # Random in area [0.1), if it is <prob, then we transmit
            if r < prob:
                n = 0                               # Recipient selection n from {1,2,3,4,5,6,7,8}
                while True:
                    n = int(random.random()  *N)
                    if n != i:                      # It must be different from the sender
                        break
                p = Packet(slot, i+1, n+1)          # Create a package with a start waiting time in the current timeslot, from node i + 1, to n + 1
                noOfPacketsGenerated = noOfPacketsGenerated + 1
                # Add to the Node queue if not full
                if len(queues[i][0])+len(queues[i][1])+len(queues[i][2])+len(queues[i][3])+len(queues[i][4])+len(queues[i][5])+len(queues[i][6])+len(queues[i][7]) < QUEUE_SIZE:
                    queues[i][n].append(p)
                else:
                    bufferFails[i] = bufferFails[i] + 1
                    if debug:
                        print("BUFFER FULL @ node " + str(i+1))
        channels = copyChannels()
        listOfNodesPerChannel = []
        slot = slot + 1
        setChannels()
        trans = schedule(channels, listOfNodesPerChannel)   # Apply an algorithm to distribute sender channels
        if debug:                                           # debugging, print node queues
            for i in range(0, 8):
                 print("\tnode#" + str(i + 1) + ":", end = " ")
                 for j in range(0, 8):
                     for k in range(0, len(queues[i][j])):
                         print(str(j + 1), end = " ")
                     print("")
        for i in range(0, N):                               # Sending packets
            if trans[i] > 0:                                # If the node transmits a packet
                k = trans[i]                                # is busy, actually we mean that it has a package in its queues
                # We check in the queues of i if it has any packages for the channel k (== trans {i]) If he doesn't, unfortunately have to wait in line. No transmission!
                l = -1
                if queues[i][2 * k - 2]:                    # In 'System 3' on channel k the nodes 2k and 2k-1 listen
                    l = 2 * k - 2
                elif queues[i][2 * k - 1]:
                    l = 2 * k - 1
                if l != -1:
                    packet = queues[i][l][0]
                    queues[i][l].pop(0)                       # Remove the package from the queue
                    packet.setSlotSent(slot)                  # We note in the package when it was sent
                    transmittedPackages.append(packet)        # Add to the list of SENT packages
                    if debug and slot==54:                    # debugging, prints variables for a random slot (eg 60)
                        print("i="+str(i)+" k="+str(k)+" l="+str(l)+" "+str(packet))
    averageDelay = calcAverageDelay(transmittedPackages)      # Calculation of the average delay
    throughput = calcThroughPut()                             # Calculation of throughput
    # Print result
    if run==1:
        print("No of Run, Probability, Throughput, Average Delay")
    print("%2d, %4f, %f, %f" % (run, prob, throughput, averageDelay))
    if debug:
        print("Number of packets created:"+str(noOfPacketsGenerated)+" Number of packets sent:"+str(len(transmittedPackages)) +" SOMETHING STRANGE : "+str(noOfPacketsGenerated-len(transmittedPackages)) + " buffer fails:", end=" ")
        for i in range(0, 8):
            print(str(bufferFails[i]) + " ", end = " ")
        print("")
    print("RUN")