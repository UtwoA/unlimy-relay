import NodesTable from '../../components/nodes-table';
import { requireAdminJson } from '../../lib/admin';

export default async function NodesPage() {
  const nodes = await requireAdminJson('/nodes');
  return <NodesTable initialNodes={nodes} />;
}
