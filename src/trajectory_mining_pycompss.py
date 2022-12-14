from datetime import date
import sys
import argparse

from parsoda import SocialDataApp
from parsoda.function.analysis.gap_bide_analysis import GapBIDE
from parsoda.function.crawling.local_file_crawler import LocalFileCrawler
from parsoda.function.crawling.parsing.flickr_parser import FlickrParser
from parsoda.function.crawling.parsing.twitter_parser import TwitterParser
from parsoda.function.crawling.parsing.vinitaly2019_parser import Vinitaly2019Parser
from parsoda.function.filtering import IsInPlace, IsInRoI

from parsoda.function.mapping.find_poi import FindPoI
from parsoda.function.reduction.reduce_by_trajectories import ReduceByTrajectories
from parsoda.function.visualization.sort_gap_bide import SortGapBIDE
from parsoda.utils.roi import RoI

from parsoda.model.driver.parsoda_singlecore_driver import ParsodaSingleCoreDriver
from parsoda.model.driver.parsoda_pycompss_driver import ParsodaPyCompssDriver

def parse_command_line():
    parser = argparse.ArgumentParser(description='Trajectory Mining application')
    parser.add_argument("partitions",
                        type=int,
                        default=8,
                        help="specifies the number of data partitions.")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_command_line()

    driver = ParsodaPyCompssDriver()
    
    app = SocialDataApp("Trajectory Mining", driver, num_partitions=args.partitions)

    app.set_crawlers([
        LocalFileCrawler('./resources/input/TwitterRome2017_100k.json', TwitterParser()),
        LocalFileCrawler('./resources/input/flickr100k.json', FlickrParser()),
        LocalFileCrawler('./resources/input/vinitaly2019.json', Vinitaly2019Parser()),
    ])
    app.set_filters([
        IsInRoI("./resources/input/RomeRoIs.kml")
    ])
    app.set_mapper(FindPoI("./resources/input/RomeRoIs.kml"))
    app.set_secondary_sort_key(lambda x: x[0])
    app.set_reducer(ReduceByTrajectories(3))
    app.set_analyzer(GapBIDE(0.01, 0, 10))
    app.set_visualizer(
        SortGapBIDE(
            "./resources/output/trajectory_mining.txt", 
            'support', 
            mode='descending', 
            min_length=3
        )
    )

    app.execute()
