import weaviate

client = weaviate.connect_to_local(skip_init_checks=True)
print(client.collections.list_all())  # List all collections

for name in client.collections.list_all():
    client.collections.delete(name)
    print(f"Deleted collection: {name}")

print(client.collections.list_all())  # Confirm deletion
client.close()