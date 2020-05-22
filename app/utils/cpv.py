from app.utils.utils import read_json


class CPV:
    """Class for CVP object representation"""

    def __init__(self, cpv_id, description=''):
        self.cpv = cpv_id
        self.section = cpv_id[:2]
        self.group = cpv_id[:3]
        self.klass = cpv_id[:4]
        self.category = cpv_id[:5]
        self.detail = cpv_id[5:]
        self.description = description

    def to_dict(self):
        return {
            'id': self.cpv,
            'scheme': 'CPV',
            'description': self.description
        }


class ClassificationTree:
    """Convert sorted CPV ids list to CVP tree"""

    def __init__(self):
        self.sections = {}
        self.groups = {}
        self.klasses = {}
        self.categories = {}
        self.details = {}
        self.cpvs = {}
        cpvs = read_json('data/uk.json')
        for cpv_id, description in cpvs.items():
            cpv = CPV(cpv_id, description)
            if '0' * 6 in cpv_id[2:]:
                cpv.type = 0  # Section
                cpv.parent = None
                self.sections[cpv.section] = cpv
                self.cpvs[cpv.cpv] = cpv
            elif '0' * 5 in cpv_id[3:]:
                cpv.type = 1  # Group
                cpv.parent = self.sections[cpv.section]
                self.groups[cpv.group] = cpv
                self.cpvs[cpv.cpv] = cpv
            elif '0' * 4 in cpv_id[4:]:
                cpv.type = 2  # Class
                cpv.parent = self.groups[cpv.group]
                self.klasses[cpv.klass] = cpv
                self.cpvs[cpv.cpv] = cpv
            elif '0' * 3 in cpv_id[5:]:
                cpv.type = 3  # Category
                if cpv.klass not in self.klasses:
                    cpv.parent = self.groups[cpv.group]
                else:
                    cpv.parent = self.klasses[cpv.klass]
                self.categories[cpv.category] = cpv
                self.cpvs[cpv.cpv] = cpv
            else:
                cpv.type = 4  # Detail
                if cpv.category not in self.categories:
                    if cpv.klass not in self.klasses:
                        if cpv.group not in self.groups:
                            cpv.parent = self.sections[cpv.section]
                        else:
                            cpv.parent = self.groups[cpv.group]
                    else:
                        cpv.parent = self.klasses[cpv.klass]
                else:
                    cpv.parent = self.categories[cpv.category]
                self.cpvs[cpv.cpv] = cpv

    def _get_cpv_by_type(self, cpv, type_level=3):
        """
        Method for getting parent cpv on type_level.
        """
        if cpv.type < type_level:
            return
        while cpv.type > type_level:
            cpv = cpv.parent
        return cpv

    def get_cpv(self, cpv_id):
        """
        Return CPV object by cpv_id or None if object missed.
        """
        return self.cpvs.get(cpv_id)

    def get_common_cpv(self, cpv_ids_list):
        """
        Return common cpv id for list cpv ids if existed else None
        """
        if len(set(cpv_ids_list)) == 1:
            return cpv_ids_list[0]
        cpvs = [self.get_cpv(i) for i in cpv_ids_list]
        min_type = min(c.type for c in cpvs)
        if min_type == 4:
            min_type = 3

        for level in range(min_type, -1, -1):
            min_type_cpvs = [self._get_cpv_by_type(c, level) for c in cpvs]
            cpv_ids = {c.cpv for c in min_type_cpvs}
            if len(cpv_ids) == 1:
                return cpv_ids.pop()
