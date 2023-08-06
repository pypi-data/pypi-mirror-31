# -*- coding: utf-8 -*-
from zebe.module.project import Project, Task, ProjectModelSession
from zebe.service.base import ModelBaseService


# 项目服务
class ProjectService(ModelBaseService):

    def __init__(self):
        super().__init__(Project, ProjectModelSession)

    # 按照年份和类型查询项目
    def find_by_year_and_type(self, year, project_type):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.type == project_type).all()
        self.session.close()
        return result

    # 按照年份和类型查询项目总数
    def count_by_year_and_type(self, year, project_type):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.type == project_type).count()
        self.session.close()
        return result

    # 更新单个任务进度
    def update_progress(self, data_id, progress):
        entity = self.session.query(self.entity).filter(self.entity.id == data_id).one_or_none()
        if entity is not None:
            entity.progress = progress
            self.session.commit()
            self.session.close()


# 任务服务
class TaskService(ModelBaseService):

    def __init__(self):
        super().__init__(Task, ProjectModelSession)