const buildInsertQuery = (tableName, keyValuePairs) => {
  const columns = Object.keys(keyValuePairs);
  const values = Object.values(keyValuePairs);
  return `
    insert into ${tableName}
    (${columns.join(",")})
    values
    (${values.join(",")})`;
};

const withExtraQuotes = (str) => `"${str}"`;

const createAdministrativeDivisionCategory = (cy) => (category) => {
  const { id, name, level } = category;
  cy.task(
    "db:query",
    buildInsertQuery("teryt_tree_category", {
      id,
      name: withExtraQuotes(name),
      slug: withExtraQuotes(name),
      level,
    })
  );
};

// We're manually setting fields that are usually handled by django-mptt.
// This function should be kept as simple as possible, as long as it serves
// its purpose.
// For a flat tree, `lft` and `rght` should not overlap. Please use the helper
// function in `administrativeDivistionUnit` to create a batch of values.
const createAdministrativeDivisionUnit = (cy) => (unit) => {
  const { name, level, category, lft, rght } = unit;
  cy.task(
    "db:query",
    buildInsertQuery("teryt_tree_jednostkaadministracyjna", {
      // Id has a length limit.
      // If substrings are not unique, DB will reject a transaction.
      id: withExtraQuotes(name.slice(-7)),
      name: withExtraQuotes(name),
      slug: withExtraQuotes(name),
      level,
      category_id: category,
      updated_on: withExtraQuotes("2010-01-01"),
      active: 1,
      lft,
      rght,
      tree_id: 0,
    })
  );
};

const createDomain = (cy) => (domain) => {
  const { id, name, active } = domain;
  cy.task(
    "db:query",
    buildInsertQuery("domains_domain", {
      id: id,
      name: withExtraQuotes(name),
      active: active ? 1 : 0,
      created: withExtraQuotes("2010-01-01"),
      modified: withExtraQuotes("2010-01-01"),
    })
  );
};

module.exports = {
  createAdministrativeDivisionCategory,
  createAdministrativeDivisionUnit,
  createDomain,
};
