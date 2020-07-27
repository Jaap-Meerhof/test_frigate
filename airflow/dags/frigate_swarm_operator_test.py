from frigate_swarm_operator import FrigateSwarmOperator

t1 = FrigateSwarmOperator(
    name="FrigateSimulatorClientTest1",
    scale=2,
    frigate_path="/home/alberto/Dropbox/alberto/projects/frigate" ,
    task_id='FrigateSimulatorClientTest1'    
)

if __name__ == "__main__":
    print("executing operator ...")
    t1.execute(context={})    
    print("done.")