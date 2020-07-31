from frigate_simulation_operator import FrigateSimulationOperator

t1 = FrigateSimulationOperator(
    name="FrigateSimulationOperator_TEST",
    simulator_id=0,    
    task_id='1'    
)

if __name__ == "__main__":
    print("executing operator ...")
    t1.execute(context={})    
    print("done.")