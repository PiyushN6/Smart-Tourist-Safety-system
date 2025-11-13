// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract DigitalIDRegistry {
    address public owner;

    enum Status { Active, Revoked, Expired }

    struct Record {
        bytes32 idHash;
        address issuer;
        Status status;
    }

    mapping(bytes32 => Record) public records;

    event Issued(bytes32 indexed idHash, address indexed issuer);
    event StatusChanged(bytes32 indexed idHash, Status status);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor() { owner = msg.sender; }

    function issue(bytes32 idHash) external onlyOwner {
        require(records[idHash].idHash == 0x0, "exists");
        records[idHash] = Record({ idHash: idHash, issuer: msg.sender, status: Status.Active });
        emit Issued(idHash, msg.sender);
    }

    function setStatus(bytes32 idHash, Status status) external onlyOwner {
        require(records[idHash].idHash != 0x0, "not found");
        records[idHash].status = status;
        emit StatusChanged(idHash, status);
    }

    function get(bytes32 idHash) external view returns (Record memory) {
        return records[idHash];
    }
}
