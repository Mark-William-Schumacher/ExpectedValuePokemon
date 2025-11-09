from core_module.prelaunch.image_downloader import download_images_to_web_root
from core_module.prelaunch.save_candidates_to_web import save_candidates_to_json_file_in_web_root
from core_module.utils.util import debug_print
from core_module.utils.file_utils import load_json_file
from web.backend.containers import AppContainer
from web.backend.db.dao.candidates_dao import CandidatesDAO
from web.backend.db.dao.psa_dao import PsaDAO
from web.backend.db.dao.sales_dao import SalesDAO
from web.backend.db.dao.set_dao import SetDAO


def pre_launch_script():
    debug_print("pre launch script")
    container = AppContainer()
    container.wire(modules=[__name__])

    candidates_dao_instance: CandidatesDAO = container.candidates_dao()
    psa_dao_instance: PsaDAO = container.psa_dao()
    set_dao_instance: SetDAO = container.set_dao()
    sales_dao_instance: SalesDAO = container.sales_dao()
    # Wire the container to the modules that need it
    candidates = candidates_dao_instance.find_profitable_candidates2(
        min_value_increase=40,
        min_psa10_price=80,
        grading_cost=40,
        min_net_gain=0
    )

    # candidates = add_ui_labels_to_candidates_json(candidates)
    candidates = download_images_to_web_root(candidates)
    # save_candidates_to_json_file_in_web_root(candidates)

if __name__ == '__main__':
    pre_launch_script()