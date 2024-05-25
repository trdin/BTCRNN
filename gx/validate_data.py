# %%
import great_expectations as gx
import sys
from great_expectations.data_context import DataContext

#context = gx.get_context()


data_context = DataContext(context_root_dir="gx")

result = data_context.run_checkpoint(checkpoint_name="my_checkpoint", batch_request=None , run_name=None)

# %%
#result = context.run_checkpoint(checkpoint_name="station_1_checkpoint")

# %%
if not result["success"]:
    print("Validation failed!")
    sys.exit(1)

print("Validation succeeded!")