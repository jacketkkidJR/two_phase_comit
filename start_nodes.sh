#!/bin/bash

# Generated script to start all nodes
echo 'Starting all nodes...'

echo -n '' > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt

# Start coordinator
echo 'Starting coordinator...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --host localhost:9010 --participant localhost:9000 --participant localhost:9001 --participant localhost:9002 --participant localhost:9003 --participant localhost:9004 --participant localhost:9005 --participant localhost:9006 --participant localhost:9007 --participant localhost:9008 --participant localhost:9009 --log-db logcoord --log-db-host localhost:8890 --batch-size 10 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/coordinator.log 2>&1 & 
COORD_PID=$!
echo "coordinator:$COORD_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 2

# Start participant 0
echo 'Starting participant 0...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 0 --host localhost:9000 --coordinator localhost:9010 --log-db lognode0 --log-db-host localhost:8880 --data-db datanode0 --data-db-host localhost:8880 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_0.log 2>&1 & 
P0_PID=$!
echo "participant0:$P0_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 1
echo 'Starting participant 1...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 1 --host localhost:9001 --coordinator localhost:9010 --log-db lognode1 --log-db-host localhost:8881 --data-db datanode1 --data-db-host localhost:8881 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_1.log 2>&1 & 
P1_PID=$!
echo "participant1:$P1_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 2
echo 'Starting participant 2...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 2 --host localhost:9002 --coordinator localhost:9010 --log-db lognode2 --log-db-host localhost:8882 --data-db datanode2 --data-db-host localhost:8882 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_2.log 2>&1 & 
P2_PID=$!
echo "participant2:$P2_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 3
echo 'Starting participant 3...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 3 --host localhost:9003 --coordinator localhost:9010 --log-db lognode3 --log-db-host localhost:8883 --data-db datanode3 --data-db-host localhost:8883 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_3.log 2>&1 & 
P3_PID=$!
echo "participant3:$P3_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 4
echo 'Starting participant 4...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 4 --host localhost:9004 --coordinator localhost:9010 --log-db lognode4 --log-db-host localhost:8884 --data-db datanode4 --data-db-host localhost:8884 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_4.log 2>&1 & 
P4_PID=$!
echo "participant4:$P4_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 5
echo 'Starting participant 5...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 5 --host localhost:9005 --coordinator localhost:9010 --log-db lognode5 --log-db-host localhost:8885 --data-db datanode5 --data-db-host localhost:8885 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_5.log 2>&1 & 
P5_PID=$!
echo "participant5:$P5_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 6
echo 'Starting participant 6...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 6 --host localhost:9006 --coordinator localhost:9010 --log-db lognode6 --log-db-host localhost:8886 --data-db datanode6 --data-db-host localhost:8886 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_6.log 2>&1 & 
P6_PID=$!
echo "participant6:$P6_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 7
echo 'Starting participant 7...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 7 --host localhost:9007 --coordinator localhost:9010 --log-db lognode7 --log-db-host localhost:8887 --data-db datanode7 --data-db-host localhost:8887 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_7.log 2>&1 & 
P7_PID=$!
echo "participant7:$P7_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 8
echo 'Starting participant 8...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 8 --host localhost:9008 --coordinator localhost:9010 --log-db lognode8 --log-db-host localhost:8888 --data-db datanode8 --data-db-host localhost:8888 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_8.log 2>&1 & 
P8_PID=$!
echo "participant8:$P8_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start participant 9
echo 'Starting participant 9...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/main.py --node-id 9 --host localhost:9009 --coordinator localhost:9010 --log-db lognode9 --log-db-host localhost:8889 --data-db datanode9 --data-db-host localhost:8889 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/participant_9.log 2>&1 & 
P9_PID=$!
echo "participant9:$P9_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt
sleep 1

# Start client
echo 'Starting client...'
nohup python3 /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/client.py --coordinator localhost:9010 --demo thermometerobservation --n-nodes 10 > /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/logs/client.log 2>&1 & 
CLIENT_PID=$!
echo "client:$CLIENT_PID" >> /Users/andrejevstafev/study/this-semester/cloud-comp/proj/two_phase_comit/node_pids.txt

echo 'All nodes started. Check log files in logs directory.'
echo 'To stop all nodes, run: python3 setup.py close'
