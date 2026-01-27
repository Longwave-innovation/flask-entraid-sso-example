# KeyCloak - Dex - SSO <!-- omit from toc -->

- [Intro](#intro)
- [Local Setup](#local-setup)
- [Startup](#startup)
- [Logs](#logs)
- [Mapping Custom](#mapping-custom)

## Intro

This example show how to configure Keycloak with Dex as Identity provider upstream.

## Local Setup

To test this locally it is mandatory to set some hostname mapping since the services are not exposed via dns but they communicate in the backend only via Docker network.

Hostnames to map:

```txt
  127.0.0.1      keycloak
  127.0.0.1      dex
```

This enables the resolution of call from the client browser to the underline services.

## Startup

```sh
docker compose up -d
```

Re-build flask app:

```sh
docker compose up -d --build
```

Re-create containers to apply config file changes:

```sh
docker compose up -d --force-recreate # All containers

docker compose up -d --force-recreate <container_name> # Specific container
```

## Logs

```sh
docker compose logs -f # All containers logs
docker compose logs -f <container_name> # Specific container logs
```

## Mapping Custom

Tramite Dex è possibile mappare dei valori customa claim standard attraverso l'attributo `claimMapping`.

In questo esempio mappiamo l'attributo `users-groups` custom al claim standard `groups`:

```yaml
 claimMapping:
    groups: user-groups
```
