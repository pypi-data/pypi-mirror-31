from colin.checks.abstract.labels import LabelCheck


class VersionCheck(LabelCheck):

    def __init__(self):
        super(self.__class__, self) \
            .__init__(name="version_label_required",
                      message="Label 'version' has to be specified.",
                      description="Version of the image.",
                      reference_url="https://fedoraproject.org/wiki/Container:Guidelines#LABELS",
                      tags=["version", "label", "required"],
                      label="version",
                      required=True,
                      value_regex=None)
