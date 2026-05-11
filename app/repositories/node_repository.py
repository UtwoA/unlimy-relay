from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Node


class NodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_nodes(self) -> list[Node]:
        return self.db.scalars(select(Node).order_by(Node.id)).all()

    def get(self, node_id: int) -> Node | None:
        return self.db.get(Node, node_id)

    def get_by_name(self, name: str) -> Node | None:
        return self.db.scalar(select(Node).where(Node.name == name))

    def healthy_nodes(self) -> list[Node]:
        return self.db.scalars(select(Node).where(Node.is_enabled.is_(True), Node.is_online.is_(True))).all()

    def save(self, node: Node) -> Node:
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete(self, node: Node) -> None:
        self.db.delete(node)
        self.db.commit()
