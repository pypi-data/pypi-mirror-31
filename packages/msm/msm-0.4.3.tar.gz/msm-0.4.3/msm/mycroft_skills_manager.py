from __future__ import print_function

import logging
from glob import glob
from itertools import chain

from multiprocessing.pool import ThreadPool
from os.path import expanduser, join, dirname
from typing import Dict, List

from msm.exceptions import MsmException, SkillNotFound, MultipleSkillMatches
from msm.skill_entry import SkillEntry
from msm.skill_repo import SkillRepo

LOG = logging.getLogger(__name__)


class MycroftSkillsManager(object):
    SKILL_GROUPS = {'default', 'mycroft_mark_1', 'picroft', 'kde'}
    DEFAULT_SKILLS_DIR = "/opt/mycroft/skills"

    def __init__(self, platform='default', skills_dir=None, repo=None,
                 versioned=True):
        self.platform = platform
        self.skills_dir = expanduser(skills_dir or '') \
            or self.DEFAULT_SKILLS_DIR
        self.repo = repo or SkillRepo()
        self.versioned = versioned

    def install(self, param, author=None):
        """Install by url or name"""
        self.find_skill(param, author).install()

    def remove(self, param, author=None):
        """Remove by url or name"""
        self.find_skill(param, author).remove()

    def update(self):
        """Update all downloaded skills"""
        def run_update(skill):
            try:
                skill.update()
                return True
            except MsmException as e:
                LOG.error('Error updating {}: {}'.format(skill, repr(e)))
                return False

        local_skills = [skill for skill in self.list() if skill.is_local]
        return all(ThreadPool().map(run_update, local_skills))

    def install_defaults(self):
        """Installs the default skills, updates all others"""
        skill_groups = self.get_defaults()

        if self.platform not in skill_groups:
            LOG.error('Unknown platform:' + self.platform)

        def install_default(skill):
            try:
                if not skill.is_local:
                    skill.install()
                else:
                    skill.update()
                return True
            except MsmException as e:
                LOG.error('Error installing {}: {}'.format(skill.name,
                                                           repr(e)))
                return False
        default_skills = chain(*[
            skill_groups.get(i, []) for i in {'default', self.platform}
        ])

        return all(ThreadPool().map(install_default, default_skills))

    def get_defaults(self):  # type: () -> Dict[str, List[SkillEntry]]
        """Returns {'skill_group': [SkillEntry('name')]}"""
        self.repo.update()
        skills = self.list()
        name_to_skill = {skill.name: skill for skill in skills}
        defaults = {group: [] for group in self.SKILL_GROUPS}

        for section_name, skill_names in self.repo.get_default_skill_names():
            section_skills = []
            for skill_name in skill_names:
                if skill_name in name_to_skill:
                    section_skills.append(name_to_skill[skill_name])
                else:
                    LOG.warning('No such default skill: ' + skill_name)
                defaults[section_name] = section_skills

        return defaults

    @staticmethod
    def _unique_skills(skills):
        return list({i.repo: i for i in skills}.values())

    def list(self):
        """
        Load a list of SkillEntry objects from both local and
        remote skills

        It is necessary to load both local and remote skills at
        the same time to correctly associate local skills with the name
        in the repo and remote skills with any custom path that they
        have been downloaded to
        """
        self.repo.update()
        remote_skill_list = (
            SkillEntry(
                name, SkillEntry.create_path(self.skills_dir, url, name),
                url, sha if self.versioned else '', msm=self
            )
            for name, path, url, sha in self.repo.get_skill_data()
        )
        remote_skills = {
            skill.id: skill for skill in remote_skill_list
        }
        all_skills = []
        for skill_file in glob(join(self.skills_dir, '*', '__init__.py')):
            skill = SkillEntry.from_folder(dirname(skill_file), msm=self)
            if skill.id in remote_skills:
                skill.attach(remote_skills.pop(skill.id))
            all_skills.append(skill)
        all_skills += list(remote_skills.values())
        return all_skills

    def find_skill(self, param, author=None, skills=None):
        # type: (str, str, List[SkillEntry]) -> SkillEntry
        """Find skill by name or url"""
        if param.startswith('https://') or param.startswith('http://'):
            self.repo.update()
            repo_id = SkillEntry.extract_repo_id(param)
            for skill in self.list():
                if skill.id == repo_id:
                    return skill
            name = SkillEntry.extract_repo_name(param)
            path = SkillEntry.create_path(self.skills_dir, param)
            return SkillEntry(name, path, param, msm=self)
        else:
            skill_confs = {
                skill: skill.match(param, author)
                for skill in skills or self.list()
            }
            best_skill, score = max(skill_confs.items(), key=lambda x: x[1])
            LOG.info('Best match ({}): {} by {}'.format(
                round(score, 2), best_skill.name, best_skill.author)
            )
            if score < 0.3:
                raise SkillNotFound(param)
            low_bound = (score * 0.7) if score != 1.0 else 1.0

            close_skills = [
                skill for skill, conf in skill_confs.items()
                if conf >= low_bound and skill != best_skill
            ]
            if close_skills:
                raise MultipleSkillMatches([best_skill] + close_skills)
            return best_skill
