from frigate_remove_operator import FrigateRemoveOperator

t1 = FrigateRemoveOperator(
    name="FrigateRemoveOperator_TEST",    
    task_id='1'    
)

if __name__ == "__main__":
    print("executing operator ...")
    t1.execute(context={})    
    print("done.")