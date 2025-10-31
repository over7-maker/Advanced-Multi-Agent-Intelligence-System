import asyncio

from kubernetes import client, config


class KubernetesLoadTest:
    def __init__(self, namespace: str = "amas") -> None:
        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()
        self.namespace = namespace
        self.k8s_apps = client.AppsV1Api()
        self.k8s_core = client.CoreV1Api()
        self.k8s_networking = client.NetworkingV1Api()

    async def simulate_pod_failures(
        self, label_selector: str = "app=amas", count: int = 2
    ) -> None:
        pods = self.k8s_core.list_namespaced_pod(
            self.namespace, label_selector=label_selector
        )
        for pod in pods.items[:count]:
            print(f"Terminating pod: {pod.metadata.name}")
            self.k8s_core.delete_namespaced_pod(
                name=pod.metadata.name, namespace=self.namespace, grace_period_seconds=0
            )
            await asyncio.sleep(30)

    async def scale_test(
        self, deployment_name: str = "amas", targets=(2, 5, 10)
    ) -> None:
        for target in targets:
            print(f"Scaling to {target} replicas")
            self.k8s_apps.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=self.namespace,
                body={"spec": {"replicas": target}},
            )
            await asyncio.sleep(60)

    async def network_partition_test(self) -> None:
        np = client.V1NetworkPolicy(
            metadata=client.V1ObjectMeta(name="partition-test"),
            spec=client.V1NetworkPolicySpec(
                pod_selector=client.V1LabelSelector(match_labels={"app": "amas"}),
                policy_types=["Ingress", "Egress"],
                ingress=[],
                egress=[],
            ),
        )
        self.k8s_networking.create_namespaced_network_policy(
            namespace=self.namespace, body=np
        )
        await asyncio.sleep(120)
        self.k8s_networking.delete_namespaced_network_policy(
            name="partition-test", namespace=self.namespace
        )
