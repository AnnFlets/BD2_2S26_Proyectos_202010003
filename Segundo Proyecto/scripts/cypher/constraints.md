**Constraints de unicidad:**

```sql
CREATE CONSTRAINT usuario_id IF NOT EXISTS
FOR (u:Usuario) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT usuario_email IF NOT EXISTS
FOR (u:Usuario) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT restaurante_id IF NOT EXISTS
FOR (r:Restaurante) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT tipococina_id IF NOT EXISTS
FOR (t:TipoCocina) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT chef_id IF NOT EXISTS
FOR (c:Chef) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT platillo_id IF NOT EXISTS
FOR (p:Platillo) REQUIRE p.id IS UNIQUE;
```

**Mostrar constraints:**

```sql
SHOW CONSTRAINTS;
```