
class RiskRuleset:
    version: str = "unknown"
    status: str = "active"       
    introduced_on: str = "unknown"
    description: str = ""

    @classmethod
    def metadata(cls):
        return {
            "version": cls.version,
            "status": cls.status,
            "introduced_on": cls.introduced_on,
            "description": cls.description,
        }

