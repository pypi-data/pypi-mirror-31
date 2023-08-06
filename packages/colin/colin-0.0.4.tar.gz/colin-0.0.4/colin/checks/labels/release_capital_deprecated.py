from colin.checks.abstract.labels import DeprecatedLabelCheck


class ReleaseLabelCapitalDeprecatedCheck(DeprecatedLabelCheck):

    def __init__(self):
        super(self.__class__, self) \
            .__init__(name="release_label_capital_deprecated",
                      message="Label 'Release' is deprecated.",
                      description="Replace with 'release'.",
                      reference_url="?????",
                      tags=["release", "label", "capital", "deprecated"],
                      old_label="Release",
                      new_label="release")
