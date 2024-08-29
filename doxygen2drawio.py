from sources import xmlExtractor
from sources import xmlExtractorWithType
from sources import txt2drawio

bWithType = False

if __name__ == '__main__':
    # if bWithType:
    #     xmlExtractorWithType.ExtractWitType()
    # else:
    xmlExtractor.Extract()
    txt2drawio.txtToDrawio()
    pass
