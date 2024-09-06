from loguru import logger as log
from utilities.string_modification import find_unique_elements,remove_redundant_elements


from_exchange_order_id= [2, 4,6]

combined_closed_open= [1, 2, 3, 4, 5]
combined=from_exchange_order_id+combined_closed_open
unrecorded_order_id =find_unique_elements(combined_closed_open, from_exchange_order_id)
unrecorded_order=list(
        set(from_exchange_order_id).difference(combined_closed_open)
    )

log.warning (f"unrecorded_order_id {unrecorded_order_id} {remove_redundant_elements(combined)} {unrecorded_order}")


from_exchange_order_id= ['77081402206', '77081224487', '77080719391', '77080693530', '77080109025']

combined_closed_open= ['76929606531', '76929612012', '76929622235', '76929625383', '76929761613', '76929775941', 
                       '76929782836', '76931796522', '76931808865', '76931826602', '76931834919', '77009487810', 
                       '76942983490', '76932075196', '76931998517', '77080719391', '77079718777', '77081402206', 
                       '77081224487', '76932021797', '76942978443', '76932073012', '76943160627', '76931961780', 
                       '76943235088', '76931965499', '76943241159', '76931974192', '76943303026', '76931987795', 
                       '76943356056', '76931997174', '77009496663', '76929537851', '77052730155', '76929580705', 
                       '77052768802', '77075019580', '77079641555']
unrecorded_order_id = list(
        set(from_exchange_order_id).difference(combined_closed_open)
    )
log.warning (f"unrecorded_order_id {unrecorded_order_id}")
