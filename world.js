class World {
  constructor(width, height, characters) {
    this.width = width;
    this.height = height;
    if(characters === undefined) {
      this.characters = [];
    }
    else {
      this.characters = characters;
    }
  }

  static populatedBy(width, height, populator) {
    let world = new World(width, height);
    for (let x = 0; x < width; x++) {
      for (let y = 0; y < height; y++) {
        world = world.withCharacterAt(populator.next(), x, y);
      }
    }

    return world;
  }

  get rows() {
    let rows = [];
    for (let rowNum = 0; rowNum < this.height; rowNum++) {
      let row = new Array(this.width);
      for (let colNum = 0; colNum < this.width; colNum++) {
        row[colNum] = this._at(colNum, rowNum);
      }
      rows.push(row);
    }
    return rows;
  }

  withCharacterAt(character, x, y) {
    const newChars = this.characters.concat([{x: x, y: y, character: character}]);
    return new World(this.width, this.height, newChars);
  }

  _at(x, y) {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) {
      return undefined;
    }
    const record = this.characters.find((r) => r.x == x && r.y == y);
    if(record === undefined) {
      return null;
    }
    return record.character;
  }
}

module.exports = World;
